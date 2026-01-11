from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.blueprints.v1.models import CheckoutRequest, OrderPath, ProductQuery
from app.container import ApplicationContainer
from app.controllers import OrderController
from app.models.order import Order

orders_bp = APIBlueprint("orders", __name__, abp_tags=[Tag(name="orders")], url_prefix="/api/v1/orders")


def _order_to_dict(order: Order, language: str | None = None) -> dict[str, Any]:
    """Convert order to dict."""
    items: list[dict[str, Any]] = []
    for item in order.items:
        translation = item.product.get_translation(language)
        product_name = translation.name if translation else item.product.name

        # Get variation name with translation and image
        variation_name = None
        image_url = item.product.image_url
        if item.variation:
            variation_translation = item.variation.get_translation(language)
            variation_name = variation_translation.name if variation_translation else item.variation.name
            if item.variation.image_url:
                image_url = item.variation.image_url

        items.append(
            {
                "product_id": item.product_id,
                "product_name": product_name,
                "image_url": image_url,
                "variation_id": item.variation_id,
                "variation_name": variation_name,
                "unit_price": str(item.unit_price),
                "quantity": item.quantity,
                "subtotal": str(item.unit_price * item.quantity),
            }
        )
    return {
        "id": order.id,
        "label": order.display_label,
        "status": order.status.value,
        "total": str(order.total),
        "notes": order.notes,
        "items": items,
        "inserted_at": order.inserted_at.isoformat() if order.inserted_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


@orders_bp.post("")
@inject
def create_order(
    body: CheckoutRequest,
    query: ProductQuery,
    order_controller: OrderController = Provide[ApplicationContainer.controllers.order],
) -> tuple[flask.Response, HTTPStatus]:
    """Create an order from cart (checkout)."""
    order = order_controller.create_order_from_cart(
        cart_token=body.cart_token,
        contact_info=body.contact_info,
        notes=body.notes,
    )
    return flask.jsonify(_order_to_dict(order, query.language)), HTTPStatus.CREATED


@orders_bp.get("/<string:order_id>")
@inject
def get_order(
    path: OrderPath,
    query: ProductQuery,
    order_controller: OrderController = Provide[ApplicationContainer.controllers.order],
) -> tuple[flask.Response, HTTPStatus]:
    """Get order by ULID."""
    order = order_controller.get_order(path.order_id)
    if not order:
        return flask.jsonify({"error": "Order not found"}), HTTPStatus.NOT_FOUND
    return flask.jsonify(_order_to_dict(order, query.language)), HTTPStatus.OK
