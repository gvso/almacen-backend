from decimal import Decimal

from ulid import ULID

from app.controllers.cart import CartController
from app.exceptions import InvalidDataError
from app.models import Order, OrderItem, OrderStatus
from app.repos import OrderRepo


class OrderController:
    def __init__(
        self,
        order_repo: OrderRepo,
        cart_controller: CartController,
    ) -> None:
        self._order_repo = order_repo
        self._cart_controller = cart_controller

    def create_order_from_cart(
        self,
        cart_token: str,
        contact_info: str | None = None,
        notes: str | None = None,
    ) -> Order:
        """Create an order from cart items."""
        cart = self._cart_controller.get_cart(cart_token)

        if not cart.items:
            raise InvalidDataError("Cart is empty")

        # Calculate total and build order items
        total = Decimal("0")
        order_items: list[OrderItem] = []
        order_id = str(ULID())

        for cart_item in cart.items:
            product = cart_item.product

            if not product.is_active:
                raise InvalidDataError(f"Product '{product.name}' is no longer available")

            item_total = product.price * cart_item.quantity
            total += item_total

            order_item = OrderItem(
                order_id=order_id,
                product_id=product.id,
                quantity=cart_item.quantity,
                unit_price=product.price,
                product_name=product.name,
            )
            order_items.append(order_item)

        # Create order
        order = Order(
            id=order_id,
            status=OrderStatus.PENDING,
            total=total,
            contact_info=contact_info,
            notes=notes,
            items=order_items,
        )

        # Save order and clear cart
        self._order_repo.persist(order, do_commit=False)
        self._cart_controller.clear_cart(cart_token)
        self._order_repo.commit()

        return order

    def get_order(self, order_id: str) -> Order | None:
        """Get order by ULID."""
        return self._order_repo.get_by_ulid(order_id)

    def confirm_order(self, order_id: str) -> Order:
        """Confirm an order."""
        order = self._order_repo.get_by_ulid(order_id)
        if not order:
            raise InvalidDataError(f"Order {order_id} not found")

        if order.status != OrderStatus.PENDING:
            raise InvalidDataError(f"Order cannot be confirmed. Current status: {order.status.value}")

        return self._order_repo.update(order, {"status": OrderStatus.CONFIRMED})

    def cancel_order(self, order_id: str) -> Order:
        """Cancel an order."""
        order = self._order_repo.get_by_ulid(order_id)
        if not order:
            raise InvalidDataError(f"Order {order_id} not found")

        if order.status == OrderStatus.CANCELLED:
            raise InvalidDataError("Order is already cancelled")

        return self._order_repo.update(order, {"status": OrderStatus.CANCELLED})
