from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel

from app.container import ApplicationContainer
from app.controllers import OrderController
from app.models.order import Order

orders_bp = APIBlueprint("orders", __name__, abp_tags=[Tag(name="orders")], url_prefix="/api/v1/orders")


class CheckoutRequest(BaseModel):
    cart_token: str
    contact_info: str | None = None
    notes: str | None = None


def _order_to_dict(order: Order) -> dict[str, Any]:
    """Convert order to dict."""
    items: list[dict[str, Any]] = []
    for item in order.items:
        items.append(
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "unit_price": str(item.unit_price),
                "quantity": item.quantity,
                "subtotal": str(item.unit_price * item.quantity),
            }
        )
    return {
        "id": order.id,
        "status": order.status.value,
        "total": str(order.total),
        "notes": order.notes,
        "items": items,
        "inserted_at": order.inserted_at.isoformat() if order.inserted_at else None,
    }


@orders_bp.post("")
@inject
def create_order(
    body: CheckoutRequest,
    order_controller: OrderController = Provide[ApplicationContainer.controllers.order],
) -> tuple[flask.Response, HTTPStatus]:
    """Create an order from cart (checkout)."""
    order = order_controller.create_order_from_cart(
        cart_token=body.cart_token,
        contact_info=body.contact_info,
        notes=body.notes,
    )
    return flask.jsonify(_order_to_dict(order)), HTTPStatus.CREATED


@orders_bp.get("/<string:order_id>")
@inject
def get_order(
    order_id: str,
    order_controller: OrderController = Provide[ApplicationContainer.controllers.order],
) -> tuple[flask.Response, HTTPStatus]:
    """Get order by ULID."""
    order = order_controller.get_order(order_id)
    if not order:
        return flask.jsonify({"error": "Order not found"}), HTTPStatus.NOT_FOUND
    return flask.jsonify(_order_to_dict(order)), HTTPStatus.OK
