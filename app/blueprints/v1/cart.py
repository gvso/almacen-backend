from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.blueprints.v1.models import (
    AddItemRequest,
    CartItemPath,
    CartPath,
    ProductQuery,
    UpdateItemRequest,
)
from app.container import ApplicationContainer
from app.controllers import CartController
from app.models.cart import Cart

cart_bp = APIBlueprint("cart", __name__, abp_tags=[Tag(name="cart")], url_prefix="/api/v1/cart")


def _cart_to_dict(cart: Cart, language: str | None = None) -> dict[str, Any]:
    """Convert cart to dict with computed total."""
    items = []
    total = 0.0
    for item in cart.items:
        item_total = float(item.product.price) * item.quantity
        total += item_total
        translation = item.product.get_translation(language)
        product_name = translation.name if translation else item.product.name
        items.append(
            {
                "product_id": item.product_id,
                "product_name": product_name,
                "product_image_url": item.product.image_url,
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
    query: ProductQuery,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Create a new cart."""
    cart = cart_controller.get_or_create_cart(None)
    return flask.jsonify(_cart_to_dict(cart, query.language)), HTTPStatus.CREATED


@cart_bp.get("/<string:token>")
@inject
def get_cart(
    path: CartPath,
    query: ProductQuery,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Get cart by token."""
    cart = cart_controller.get_cart(path.token)
    return flask.jsonify(_cart_to_dict(cart, query.language)), HTTPStatus.OK


@cart_bp.post("/<string:token>/items")
@inject
def add_item(
    path: CartPath,
    body: AddItemRequest,
    query: ProductQuery,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Add an item to the cart."""
    cart = cart_controller.add_item(path.token, body.product_id, body.quantity)
    return flask.jsonify(_cart_to_dict(cart, query.language)), HTTPStatus.OK


@cart_bp.put("/<string:token>/items/<int:product_id>")
@inject
def update_item(
    path: CartItemPath,
    body: UpdateItemRequest,
    query: ProductQuery,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Update item quantity in cart."""
    cart = cart_controller.update_item_quantity(path.token, path.product_id, body.quantity)
    return flask.jsonify(_cart_to_dict(cart, query.language)), HTTPStatus.OK


@cart_bp.delete("/<string:token>/items/<int:product_id>")
@inject
def remove_item(
    path: CartItemPath,
    cart_controller: CartController = Provide[ApplicationContainer.controllers.cart],
) -> tuple[flask.Response, HTTPStatus]:
    """Remove an item from the cart."""
    cart_controller.remove_item(path.token, path.product_id)
    return flask.jsonify({"status": "success"}), HTTPStatus.OK
