from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.blueprints.v1.models import ProductPath, ProductQuery
from app.container import ApplicationContainer
from app.repos import ProductRepo

products_bp = APIBlueprint("products", __name__, abp_tags=[Tag(name="products")], url_prefix="/api/v1/products")


@products_bp.get("")
@inject
def list_products(
    query: ProductQuery,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Get all available products. Optionally filter by type (product or service)."""
    products_query = product_repo.get_all_active(product_type=query.type)

    if query.search:
        search_term = f"%{query.search.lower()}%"
        products_query = product_repo.filter_by_search(products_query, search_term, query.language)

    products = products_query.all()
    data: list[dict[str, Any]] = [product.to_dict_with_language(query.language) for product in products]
    return flask.jsonify({"data": data}), HTTPStatus.OK


@products_bp.get("/<int:product_id>")
@inject
def get_product(
    path: ProductPath,
    query: ProductQuery,
    product_repo: ProductRepo = Provide[ApplicationContainer.repos.product],
) -> tuple[flask.Response, HTTPStatus]:
    """Get a specific product by ID."""
    product = product_repo.get(str(path.product_id))
    if not product or not product.is_active:
        return flask.jsonify({"error": "Product not found"}), HTTPStatus.NOT_FOUND
    return flask.jsonify(product.to_dict_with_language(query.language)), HTTPStatus.OK
