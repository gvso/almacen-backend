from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag as OpenApiTag

from app.blueprints.v1.models import (
    TipCreate,
    TipPath,
    TipQuery,
    TipReorderRequest,
    TipTranslationCreate,
    TipTranslationPath,
    TipUpdate,
)
from app.container import ApplicationContainer
from app.db import db
from app.middlewares.admin_auth import require_admin_auth
from app.models.tip import Tip, TipTranslation
from app.repos.tip import TipRepo

admin_tips_bp = APIBlueprint(
    "admin_tips",
    __name__,
    abp_tags=[OpenApiTag(name="admin-tips")],
    url_prefix="/api/v1/admin/tips",
)


# ============ Helper Functions ============


def tip_to_admin_dict(tip: Tip) -> dict[str, Any]:
    """Convert tip to dict with all translations and tags for admin."""
    data = tip.as_dict()
    data["translations"] = [
        {"language": t.language, "title": t.title, "description": t.description} for t in tip.translations
    ]
    data["tags"] = [
        {
            **tag.as_dict(),
            "translations": [{"language": t.language, "label": t.label} for t in tag.translations],
        }
        for tag in tip.tags
    ]
    return data


# ============ Tip Endpoints ============


@admin_tips_bp.get("")
@require_admin_auth
@inject
def list_tips(
    query: TipQuery,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """List all tips for admin management, optionally filtered by tip_type."""
    tips = tip_repo.get_all(tip_type=query.tip_type).all()
    data = [tip_to_admin_dict(t) for t in tips]
    return flask.jsonify({"data": data}), HTTPStatus.OK


@admin_tips_bp.post("")
@require_admin_auth
@inject
def create_tip(
    body: TipCreate,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Create a new tip."""
    # Set order to be after all existing tips if not specified
    order = body.order
    if order == 0:
        max_order = tip_repo.get_max_order()
        order = max_order + 1

    tip = Tip(
        title=body.title,
        description=body.description,
        image_url=body.image_url,
        order=order,
        is_active=body.is_active,
        tip_type=body.tip_type,
    )
    tip_repo.persist(tip)
    return flask.jsonify(tip_to_admin_dict(tip)), HTTPStatus.CREATED


@admin_tips_bp.get("/<int:tip_id>")
@require_admin_auth
@inject
def get_tip(
    path: TipPath,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Get a specific tip by ID."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND
    return flask.jsonify(tip_to_admin_dict(tip)), HTTPStatus.OK


@admin_tips_bp.put("/<int:tip_id>")
@require_admin_auth
@inject
def update_tip(
    path: TipPath,
    body: TipUpdate,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Update a tip's fields."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        tip_repo.update(tip, update_data)

    return flask.jsonify(tip_to_admin_dict(tip)), HTTPStatus.OK


@admin_tips_bp.delete("/<int:tip_id>")
@require_admin_auth
@inject
def delete_tip(
    path: TipPath,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a tip."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(tip)
    db.session.commit()
    return flask.jsonify({"status": "deleted"}), HTTPStatus.OK


@admin_tips_bp.patch("/reorder")
@require_admin_auth
@inject
def reorder_tips(
    body: TipReorderRequest,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Bulk update tip order positions."""
    for item in body.items:
        tip = tip_repo.get(item.id)
        if tip:
            tip.order = item.order
    db.session.commit()

    tips = tip_repo.get_all().all()
    data = [tip_to_admin_dict(t) for t in tips]
    return flask.jsonify({"data": data}), HTTPStatus.OK


# ============ Tip Translation Endpoints ============


@admin_tips_bp.post("/<int:tip_id>/translations")
@require_admin_auth
@inject
def create_or_update_tip_translation(
    path: TipPath,
    body: TipTranslationCreate,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Create or update a tip translation."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND

    # Check if translation exists
    existing = next((t for t in tip.translations if t.language == body.language), None)
    if existing:
        existing.title = body.title
        existing.description = body.description
    else:
        translation = TipTranslation(
            tip_id=tip.id,
            language=body.language,
            title=body.title,
            description=body.description,
        )
        db.session.add(translation)

    db.session.commit()
    db.session.expire(tip)
    db.session.refresh(tip)
    return flask.jsonify(tip_to_admin_dict(tip)), HTTPStatus.OK


@admin_tips_bp.delete("/<int:tip_id>/translations/<language>")
@require_admin_auth
@inject
def delete_tip_translation(
    path: TipTranslationPath,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a tip translation."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND

    translation = next((t for t in tip.translations if t.language == path.language), None)
    if not translation:
        return (
            flask.jsonify({"error": "not_found", "error_description": "Translation not found"}),
            HTTPStatus.NOT_FOUND,
        )

    db.session.delete(translation)
    db.session.commit()
    db.session.refresh(tip)
    return flask.jsonify(tip_to_admin_dict(tip)), HTTPStatus.OK
