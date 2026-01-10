from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.container import ApplicationContainer
from app.repos import ProductRepo

products_bp = APIBlueprint("products", __name__, abp_tags=[Tag(name="products")], url_prefix="/api/v1/products")


@products_bp.get("")
@inject
def list_products(
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Get all available products."""
    products = product_repo.get_all_active().all()
    data: list[dict[str, Any]] = [product.as_dict() for product in products]
    return flask.jsonify({"data": data}), HTTPStatus.OK


@products_bp.get("/<int:product_id>")
@inject
def get_product(
    product_id: int,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Get a specific product by ID."""
    product = product_repo.get(str(product_id))
    if not product or not product.is_active:
        return flask.jsonify({"error": "Product not found"}), HTTPStatus.NOT_FOUND
    return flask.jsonify(product.as_dict()), HTTPStatus.OK
