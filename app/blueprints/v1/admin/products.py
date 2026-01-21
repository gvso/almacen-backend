from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.container import ApplicationContainer
from app.controllers import ProductController
from app.db import db
from app.middlewares.admin_auth import require_admin_auth
from app.models import (
    Product,
    ProductTranslation,
    ProductVariation,
    ProductVariationTranslation,
)
from app.repos import ProductRepo, ProductVariationRepo

from .models import (
    AdminProductQuery,
    ProductCreate,
    ProductPath,
    ProductUpdate,
    ReorderRequest,
    TranslationCreate,
    TranslationPath,
    VariationCreate,
    VariationPath,
    VariationTranslationCreate,
    VariationTranslationDeletePath,
    VariationTranslationPath,
    VariationUpdate,
)

products_bp = APIBlueprint(
    "admin_products",
    __name__,
    abp_tags=[Tag(name="admin-products")],
    url_prefix="/api/v1/admin/products",
)


def product_to_admin_dict(product: Product) -> dict[str, Any]:
    """Convert product to dict with all translations, variations, and tags for admin."""
    data = product.as_dict()
    data["translations"] = [
        {"language": t.language, "name": t.name, "description": t.description} for t in product.translations
    ]
    data["variations"] = [
        {
            **v.as_dict(),
            "translations": [{"language": t.language, "name": t.name} for t in v.translations],
        }
        for v in product.variations
    ]
    data["tags"] = [
        {
            **tag.as_dict(),
            "translations": [{"language": t.language, "label": t.label} for t in tag.translations],
        }
        for tag in product.tags
    ]
    return data


# ============ Product Endpoints ============


@products_bp.get("")
@require_admin_auth
@inject
def list_products(
    query: AdminProductQuery,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """List all products (including inactive) for admin management. Optionally filter by type, search, or tags."""
    products_query = product_repo.get_query().order_by(Product.order, Product.inserted_at)

    if query.type:
        products_query = product_repo.filter_by_type(products_query, query.type)

    if query.search:
        search_term = f"%{query.search.lower()}%"
        products_query = product_repo.filter_by_search(products_query, search_term)

    if query.tag_ids:
        # Parse comma-separated tag IDs
        tag_id_list = [int(tid.strip()) for tid in query.tag_ids.split(",") if tid.strip().isdigit()]
        if tag_id_list:
            products_query = product_repo.filter_by_tags(products_query, tag_id_list)

    products = products_query.all()
    data = [product_to_admin_dict(p) for p in products]
    return flask.jsonify({"data": data}), HTTPStatus.OK


@products_bp.post("")
@require_admin_auth
@inject
def create_product(
    body: ProductCreate,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Create a new product."""
    product = Product(
        name=body.name,
        description=body.description,
        price=body.price,
        image_url=body.image_url,
        order=body.order,
        is_active=body.is_active,
        type=body.type,
    )
    product_repo.persist(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.CREATED


@products_bp.put("/<int:product_id>")
@require_admin_auth
@inject
def update_product(
    path: ProductPath,
    body: ProductUpdate,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Update a product's fields."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        product_repo.update(product, update_data)

    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK


@products_bp.delete("/<int:product_id>")
@require_admin_auth
@inject
def delete_product(
    path: ProductPath,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a product."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(product)
    db.session.commit()
    return flask.jsonify({"status": "deleted"}), HTTPStatus.OK


@products_bp.post("/<int:product_id>/clone")
@require_admin_auth
@inject
def clone_product(
    path: ProductPath,
    product_controller: ProductController = Provide[ApplicationContainer.controllers.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Clone a product with all its translations, variations, and tag associations."""
    cloned_product = product_controller.clone_product(path.product_id)
    if not cloned_product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    return flask.jsonify(product_to_admin_dict(cloned_product)), HTTPStatus.CREATED


@products_bp.patch("/reorder")
@require_admin_auth
@inject
def reorder_products(
    body: ReorderRequest,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Bulk update product order positions."""
    for item in body.items:
        product = product_repo.get(item.id)
        if product:
            product.order = item.order
    db.session.commit()

    products = product_repo.get_query().order_by(Product.order, Product.inserted_at).all()
    data = [product_to_admin_dict(p) for p in products]
    return flask.jsonify({"data": data}), HTTPStatus.OK


# ============ Product Translation Endpoints ============


@products_bp.post("/<int:product_id>/translations")
@require_admin_auth
@inject
def create_or_update_translation(
    path: ProductPath,
    body: TranslationCreate,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Create or update a product translation."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    # Check if translation exists
    existing = next((t for t in product.translations if t.language == body.language), None)
    if existing:
        existing.name = body.name
        existing.description = body.description
    else:
        translation = ProductTranslation(
            product_id=product.id,
            language=body.language,
            name=body.name,
            description=body.description,
        )
        db.session.add(translation)

    db.session.commit()
    db.session.expire(product)
    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK


@products_bp.delete("/<int:product_id>/translations/<language>")
@require_admin_auth
@inject
def delete_translation(
    path: TranslationPath,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a product translation."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    translation = next((t for t in product.translations if t.language == path.language), None)
    if not translation:
        return (
            flask.jsonify({"error": "not_found", "error_description": "Translation not found"}),
            HTTPStatus.NOT_FOUND,
        )

    db.session.delete(translation)
    db.session.commit()
    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK


# ============ Product Variation Endpoints ============


@products_bp.post("/<int:product_id>/variations")
@require_admin_auth
@inject
def create_variation(
    path: ProductPath,
    body: VariationCreate,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Create a new product variation."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    variation = ProductVariation(
        product_id=product.id,
        name=body.name,
        price=body.price,
        image_url=body.image_url,
        order=body.order or 0,
        is_active=body.is_active,
    )
    db.session.add(variation)
    db.session.commit()
    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.CREATED


@products_bp.put("/<int:product_id>/variations/<int:variation_id>")
@require_admin_auth
@inject
def update_variation(
    path: VariationPath,
    body: VariationUpdate,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
    variation_repo: ProductVariationRepo = Provide[ApplicationContainer.repos.product_variation],
) -> tuple[flask.Response, HTTPStatus]:
    """Update a product variation."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    variation = variation_repo.get(path.variation_id)
    if not variation or variation.product_id != product.id:
        return flask.jsonify({"error": "not_found", "error_description": "Variation not found"}), HTTPStatus.NOT_FOUND

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        variation_repo.update(variation, update_data)

    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK


@products_bp.delete("/<int:product_id>/variations/<int:variation_id>")
@require_admin_auth
@inject
def delete_variation(
    path: VariationPath,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
    variation_repo: ProductVariationRepo = Provide[ApplicationContainer.repos.product_variation],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a product variation."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    variation = variation_repo.get(path.variation_id)
    if not variation or variation.product_id != product.id:
        return flask.jsonify({"error": "not_found", "error_description": "Variation not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(variation)
    db.session.commit()
    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK


@products_bp.patch("/<int:product_id>/variations/reorder")
@require_admin_auth
@inject
def reorder_variations(
    path: ProductPath,
    body: ReorderRequest,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
    variation_repo: ProductVariationRepo = Provide[ApplicationContainer.repos.product_variation],
) -> tuple[flask.Response, HTTPStatus]:
    """Bulk update variation order positions for a product."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    for item in body.items:
        variation = variation_repo.get(item.id)
        if variation and variation.product_id == product.id:
            variation.order = item.order
    db.session.commit()

    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK


# ============ Variation Translation Endpoints ============


@products_bp.post("/<int:product_id>/variations/<int:variation_id>/translations")
@require_admin_auth
@inject
def create_or_update_variation_translation(
    path: VariationTranslationPath,
    body: VariationTranslationCreate,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
    variation_repo: ProductVariationRepo = Provide[ApplicationContainer.repos.product_variation],
) -> tuple[flask.Response, HTTPStatus]:
    """Create or update a variation translation."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    variation = variation_repo.get(path.variation_id)
    if not variation or variation.product_id != product.id:
        return flask.jsonify({"error": "not_found", "error_description": "Variation not found"}), HTTPStatus.NOT_FOUND

    # Check if translation exists
    existing = next((t for t in variation.translations if t.language == body.language), None)
    if existing:
        existing.name = body.name
    else:
        translation = ProductVariationTranslation(
            variation_id=variation.id,
            language=body.language,
            name=body.name,
        )
        db.session.add(translation)

    db.session.commit()
    # Expire and refresh to reload relationships
    db.session.expire(variation)
    db.session.expire(product)
    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK


@products_bp.delete("/<int:product_id>/variations/<int:variation_id>/translations/<language>")
@require_admin_auth
@inject
def delete_variation_translation(
    path: VariationTranslationDeletePath,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
    variation_repo: ProductVariationRepo = Provide[ApplicationContainer.repos.product_variation],
) -> tuple[flask.Response, HTTPStatus]:
    """Delete a variation translation."""
    product = product_repo.get(path.product_id)
    if not product:
        return flask.jsonify({"error": "not_found", "error_description": "Product not found"}), HTTPStatus.NOT_FOUND

    variation = variation_repo.get(path.variation_id)
    if not variation or variation.product_id != product.id:
        return flask.jsonify({"error": "not_found", "error_description": "Variation not found"}), HTTPStatus.NOT_FOUND

    translation = next((t for t in variation.translations if t.language == path.language), None)
    if not translation:
        return (
            flask.jsonify({"error": "not_found", "error_description": "Translation not found"}),
            HTTPStatus.NOT_FOUND,
        )

    db.session.delete(translation)
    db.session.commit()
    db.session.expire(variation)
    db.session.refresh(product)
    return flask.jsonify(product_to_admin_dict(product)), HTTPStatus.OK
