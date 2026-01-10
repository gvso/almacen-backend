from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel

from app.container import ApplicationContainer
from app.controllers import CartController
from app.models.cart import Cart

cart_bp = APIBlueprint("cart", __name__, abp_tags=[Tag(name="cart")], url_prefix="/api/v1/cart")


class AddItemRequest(BaseModel):
    product_id: int
    quantity: int = 1


class UpdateItemRequest(BaseModel):
    quantity: int


def _cart_to_dict(cart: Cart) -> dict[str, Any]:
    """Convert cart to dict with computed total."""
    items = []
    total = 0
    for item in cart.items:
        item_total = float(item.product.price) * item.quantity
        total += item_total
        items.append(
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "unit_price": str(item.product.price),
                "quantity": item.quantity,
                "subtotal": str(round(item_total, 2)),
            }
        )
    return {
        "token": cart.token,
        "items": items,
        "total": str(round(total, 2)),
    }


@cart_bp.post("")
@inject
def create_cart(
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Create a new cart."""
    cart = cart_controller.get_or_create_cart(None)
    return flask.jsonify(_cart_to_dict(cart)), HTTPStatus.CREATED


@cart_bp.get("/<string:token>")
@inject
def get_cart(
    token: str,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Get cart by token."""
    cart = cart_controller.get_cart(token)
    return flask.jsonify(_cart_to_dict(cart)), HTTPStatus.OK


@cart_bp.post("/<string:token>/items")
@inject
def add_item(
    token: str,
    body: AddItemRequest,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Add an item to the cart."""
    cart = cart_controller.add_item(token, body.product_id, body.quantity)
    return flask.jsonify(_cart_to_dict(cart)), HTTPStatus.OK


@cart_bp.put("/<string:token>/items/<int:product_id>")
@inject
def update_item(
    token: str,
    product_id: int,
    body: UpdateItemRequest,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Update item quantity in cart."""
    cart = cart_controller.update_item_quantity(token, product_id, body.quantity)
    return flask.jsonify(_cart_to_dict(cart)), HTTPStatus.OK


@cart_bp.delete("/<string:token>/items/<int:product_id>")
@inject
def remove_item(
    token: str,
    product_id: int,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Remove an item from the cart."""
    cart = cart_controller.remove_item(token, product_id)
    return flask.jsonify(_cart_to_dict(cart)), HTTPStatus.OK
