from http import HTTPStatus
from typing import Any

import flask
import sqlalchemy as sa
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.container import ApplicationContainer
from app.db import db
from app.middlewares.admin_auth import require_admin_auth
from app.models import Order
from app.models.order import OrderStatus
from app.repos import OrderRepo

from .models import OrderPath, OrderStatusUpdate, OrderUpdate

orders_bp = APIBlueprint(
    "admin_orders",
    __name__,
    abp_tags=[Tag(name="admin-orders")],
    url_prefix="/api/v1/admin/orders",
)


def _order_to_admin_dict(order: Order) -> dict[str, Any]:
    """Convert order to dict for admin view."""
    items: list[dict[str, Any]] = []
    for item in order.items:
        product_name = item.product.name
        variation_name = None
        image_url = item.product.image_url

        if item.variation:
            variation_name = item.variation.name
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


# Define custom sort order for status
STATUS_SORT_ORDER = {
    OrderStatus.confirmed: 0,
    OrderStatus.processed: 1,
    OrderStatus.cancelled: 2,
}


@orders_bp.get("")
@require_admin_auth
@inject
def list_orders(
    order_repo: OrderRepo = Provide[ApplicationContainer.repos.order],
) -> tuple[flask.Response, HTTPStatus]:
    """List all orders sorted by status (confirmed, processed, cancelled) and updated date."""
    # Use CASE expression for custom status ordering
    status_order = sa.case(
        STATUS_SORT_ORDER,
        value=Order.status,
    )
    orders = order_repo.get_query().order_by(status_order, Order.updated_at.desc()).all()
    data = [_order_to_admin_dict(o) for o in orders]
    return flask.jsonify({"data": data}), HTTPStatus.OK


@orders_bp.get("/<string:order_id>")
@require_admin_auth
@inject
def get_order(
    path: OrderPath,
    order_repo: OrderRepo = Provide[ApplicationContainer.repos.order],
) -> tuple[flask.Response, HTTPStatus]:
    """Get order by ID."""
    order = order_repo.get_by_ulid(path.order_id)
    if not order:
        return flask.jsonify({"error": "not_found", "error_description": "Order not found"}), HTTPStatus.NOT_FOUND
    return flask.jsonify(_order_to_admin_dict(order)), HTTPStatus.OK


@orders_bp.patch("/<string:order_id>/status")
@require_admin_auth
@inject
def update_order_status(
    path: OrderPath,
    body: OrderStatusUpdate,
    order_repo: OrderRepo = Provide[ApplicationContainer.repos.order],
) -> tuple[flask.Response, HTTPStatus]:
    """Update order status."""
    order = order_repo.get_by_ulid(path.order_id)
    if not order:
        return flask.jsonify({"error": "not_found", "error_description": "Order not found"}), HTTPStatus.NOT_FOUND

    order.status = body.status
    db.session.commit()
    db.session.refresh(order)

    return flask.jsonify(_order_to_admin_dict(order)), HTTPStatus.OK


@orders_bp.patch("/<string:order_id>")
@require_admin_auth
@inject
def update_order(
    path: OrderPath,
    body: OrderUpdate,
    order_repo: OrderRepo = Provide[ApplicationContainer.repos.order],
) -> tuple[flask.Response, HTTPStatus]:
    """Update order fields (e.g., label)."""
    order = order_repo.get_by_ulid(path.order_id)
    if not order:
        return flask.jsonify({"error": "not_found", "error_description": "Order not found"}), HTTPStatus.NOT_FOUND

    if body.label is not None:
        # Allow empty string to reset to default (order ID)
        order.label = body.label if body.label else None

    db.session.commit()
    db.session.refresh(order)

    return flask.jsonify(_order_to_admin_dict(order)), HTTPStatus.OK
