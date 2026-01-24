from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag as OpenApiTag
from pydantic import BaseModel, Field

from app.container import ApplicationContainer
from app.db import db
from app.middlewares.admin_auth import require_admin_auth
from app.models.tag import EntityType, Tag, TagTranslation
from app.repos import EntityTagRepo, ProductRepo, TagRepo, TipRepo

tags_bp = APIBlueprint(
    "admin_tags",
    __name__,
    abp_tags=[OpenApiTag(name="admin-tags")],
    url_prefix="/api/v1/admin/tags",
)


# ============ Request/Response Models ============


class TagPath(BaseModel):
    tag_id: int


class TagTranslationPath(BaseModel):
    tag_id: int
    language: str


class TagCreate(BaseModel):
    label: str = Field(..., max_length=100)


class TagUpdate(BaseModel):
    label: str | None = Field(None, max_length=100)


class TagTranslationCreate(BaseModel):
    language: str = Field(..., max_length=5)
    label: str = Field(..., max_length=100)


class ProductTagPath(BaseModel):
    product_id: int


class ProductTagItemPath(BaseModel):
    product_id: int
    tag_id: int


class EntityTagAdd(BaseModel):
    tag_id: int = Field(..., description="ID of the tag to add")


class TipTagPath(BaseModel):
    tip_id: int


class TipTagItemPath(BaseModel):
    tip_id: int
    tag_id: int


class ReorderItem(BaseModel):
    id: int = Field(..., description="ID of the tag")
    order: int = Field(..., description="New order position")


class ReorderRequest(BaseModel):
    items: list[ReorderItem] = Field(..., description="List of tags with their new order positions")


# ============ Helper Functions ============


def tag_to_admin_dict(tag: Tag) -> dict[str, Any]:
    """Convert tag to dict with all translations for admin."""
    data = tag.as_dict()
    data["translations"] = [{"language": t.language, "label": t.label} for t in tag.translations]
    return data


# ============ Tag Endpoints ============


@tags_bp.get("")
@require_admin_auth
@inject
def list_tags(
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """List all tags for admin management."""
    tags = tag_repo.get_all().all()
    data = [tag_to_admin_dict(t) for t in tags]
    return flask.jsonify({"data": data}), HTTPStatus.OK


@tags_bp.post("")
@require_admin_auth
@inject
def create_tag(
    body: TagCreate,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Create a new tag."""
    # Check if tag with same label exists
    existing = tag_repo.get_by_label(body.label)
    if existing:
        return (
            flask.jsonify({"error": "duplicate", "error_description": "A tag with this label already exists"}),
            HTTPStatus.CONFLICT,
        )

    # Set order to be after all existing tags
    max_order = tag_repo.get_max_order()
    tag = Tag(label=body.label, order=max_order + 1)
    tag_repo.persist(tag)
    return flask.jsonify(tag_to_admin_dict(tag)), HTTPStatus.CREATED


@tags_bp.get("/<int:tag_id>")
@require_admin_auth
@inject
def get_tag(
    path: TagPath,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Get a specific tag by ID."""
    tag = tag_repo.get(path.tag_id)
    if not tag:
        return flask.jsonify({"error": "not_found", "error_description": "Tag not found"}), HTTPStatus.NOT_FOUND
    return flask.jsonify(tag_to_admin_dict(tag)), HTTPStatus.OK


@tags_bp.put("/<int:tag_id>")
@require_admin_auth
@inject
def update_tag(
    path: TagPath,
    body: TagUpdate,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Update a tag's fields."""
    tag = tag_repo.get(path.tag_id)
    if not tag:
        return flask.jsonify({"error": "not_found", "error_description": "Tag not found"}), HTTPStatus.NOT_FOUND

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        # Check if new label conflicts with existing tag
        if "label" in update_data:
            existing = tag_repo.get_by_label(update_data["label"])
            if existing and existing.id != tag.id:
                return (
                    flask.jsonify({"error": "duplicate", "error_description": "A tag with this label already exists"}),
                    HTTPStatus.CONFLICT,
                )
        tag_repo.update(tag, update_data)

    return flask.jsonify(tag_to_admin_dict(tag)), HTTPStatus.OK


@tags_bp.delete("/<int:tag_id>")
@require_admin_auth
@inject
def delete_tag(
    path: TagPath,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a tag."""
    tag = tag_repo.get(path.tag_id)
    if not tag:
        return flask.jsonify({"error": "not_found", "error_description": "Tag not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(tag)
    db.session.commit()
    return flask.jsonify({"status": "deleted"}), HTTPStatus.OK


@tags_bp.patch("/reorder")
@require_admin_auth
@inject
def reorder_tags(
    body: ReorderRequest,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Bulk update tag order positions."""
    for item in body.items:
        tag = tag_repo.get(item.id)
        if tag:
            tag.order = item.order
    db.session.commit()

    tags = tag_repo.get_all().all()
    data = [tag_to_admin_dict(t) for t in tags]
    return flask.jsonify({"data": data}), HTTPStatus.OK


# ============ Tag Translation Endpoints ============


@tags_bp.post("/<int:tag_id>/translations")
@require_admin_auth
@inject
def create_or_update_tag_translation(
    path: TagPath,
    body: TagTranslationCreate,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Create or update a tag translation."""
    tag = tag_repo.get(path.tag_id)
    if not tag:
        return flask.jsonify({"error": "not_found", "error_description": "Tag not found"}), HTTPStatus.NOT_FOUND

    # Check if translation exists
    existing = next((t for t in tag.translations if t.language == body.language), None)
    if existing:
        existing.label = body.label
    else:
        translation = TagTranslation(
            tag_id=tag.id,
            language=body.language,
            label=body.label,
        )
        db.session.add(translation)

    db.session.commit()
    db.session.expire(tag)
    db.session.refresh(tag)
    return flask.jsonify(tag_to_admin_dict(tag)), HTTPStatus.OK


@tags_bp.delete("/<int:tag_id>/translations/<language>")
@require_admin_auth
@inject
def delete_tag_translation(
    path: TagTranslationPath,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a tag translation."""
    tag = tag_repo.get(path.tag_id)
    if not tag:
        return flask.jsonify({"error": "not_found", "error_description": "Tag not found"}), HTTPStatus.NOT_FOUND

    translation = next((t for t in tag.translations if t.language == path.language), None)
    if not translation:
        return (
            flask.jsonify({"error": "not_found", "error_description": "Translation not found"}),
            HTTPStatus.NOT_FOUND,
        )

    db.session.delete(translation)
    db.session.commit()
    db.session.refresh(tag)
    return flask.jsonify(tag_to_admin_dict(tag)), HTTPStatus.OK


# ============ Product Tags Endpoints ============


@tags_bp.get("/products/<int:product_id>")
@require_admin_auth
@inject
def get_product_tags(
    path: ProductTagPath,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Get all tags assigned to a product."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    return flask.jsonify({"data": [tag_to_admin_dict(t) for t in product.tags]}), HTTPStatus.OK


@tags_bp.post("/products/<int:product_id>")
@require_admin_auth
@inject
def add_product_tag(
    path: ProductTagPath,
    body: EntityTagAdd,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
    entity_tag_repo: EntityTagRepo = Provide[ApplicationContainer.repos.entity_tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Add a tag to a product."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    tag = tag_repo.get(body.tag_id)
    if not tag:
        return flask.jsonify({"error": "not_found", "error_description": "Tag not found"}), HTTPStatus.NOT_FOUND

    # Add the tag if not already assigned
    if not entity_tag_repo.exists(EntityType.product, product.id, tag.id):
        entity_tag_repo.add_tag(EntityType.product, product.id, tag.id)
        db.session.refresh(product)

    return flask.jsonify({"data": [tag_to_admin_dict(t) for t in product.tags]}), HTTPStatus.OK


@tags_bp.delete("/products/<int:product_id>/tags/<int:tag_id>")
@require_admin_auth
@inject
def remove_product_tag(
    path: ProductTagItemPath,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
    entity_tag_repo: EntityTagRepo = Provide[ApplicationContainer.repos.entity_tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Remove a tag from a product."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    # Find and delete the entity tag
    deleted = entity_tag_repo.remove_tag(EntityType.product, product.id, path.tag_id)

    if not deleted:
        return flask.jsonify(
            {"error": "not_found", "error_description": "Tag not assigned to product"}
        ), HTTPStatus.NOT_FOUND

    # Refresh product to get updated tags
    db.session.refresh(product)

    return flask.jsonify({"data": [tag_to_admin_dict(t) for t in product.tags]}), HTTPStatus.OK


# ============ Tip Tags Endpoints ============


@tags_bp.get("/tips/<int:tip_id>")
@require_admin_auth
@inject
def get_tip_tags(
    path: TipTagPath,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Get all tags assigned to a tip."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND

    return flask.jsonify({"data": [tag_to_admin_dict(t) for t in tip.tags]}), HTTPStatus.OK


@tags_bp.post("/tips/<int:tip_id>")
@require_admin_auth
@inject
def add_tip_tag(
    path: TipTagPath,
    body: EntityTagAdd,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
    entity_tag_repo: EntityTagRepo = Provide[ApplicationContainer.repos.entity_tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Add a tag to a tip."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND

    tag = tag_repo.get(body.tag_id)
    if not tag:
        return flask.jsonify({"error": "not_found", "error_description": "Tag not found"}), HTTPStatus.NOT_FOUND

    # Add the tag if not already assigned
    if not entity_tag_repo.exists(EntityType.tip, tip.id, tag.id):
        entity_tag_repo.add_tag(EntityType.tip, tip.id, tag.id)
        db.session.refresh(tip)

    return flask.jsonify({"data": [tag_to_admin_dict(t) for t in tip.tags]}), HTTPStatus.OK


@tags_bp.delete("/tips/<int:tip_id>/tags/<int:tag_id>")
@require_admin_auth
@inject
def remove_tip_tag(
    path: TipTagItemPath,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
    entity_tag_repo: EntityTagRepo = Provide[ApplicationContainer.repos.entity_tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Remove a tag from a tip."""
    tip = tip_repo.get(path.tip_id)
    if not tip:
        return flask.jsonify({"error": "not_found", "error_description": "Tip not found"}), HTTPStatus.NOT_FOUND

    # Find and delete the entity tag
    deleted = entity_tag_repo.remove_tag(EntityType.tip, tip.id, path.tag_id)

    if not deleted:
        return flask.jsonify(
            {"error": "not_found", "error_description": "Tag not assigned to tip"}
        ), HTTPStatus.NOT_FOUND

    # Refresh tip to get updated tags
    db.session.refresh(tip)

    return flask.jsonify({"data": [tag_to_admin_dict(t) for t in tip.tags]}), HTTPStatus.OK
