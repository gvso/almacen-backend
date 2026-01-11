from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId
from app.models.decorators.types import EnumStringType

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.product_variation import ProductVariation


class OrderStatus(str, Enum):
    confirmed = "confirmed"
    processed = "processed"
    cancelled = "cancelled"


class Order(ModelWithDates):
    """Order with ULID as primary key for easy sharing."""

    __tablename__ = "orders"

    # ULID stored as string (26 characters)
    id: Mapped[str] = mapped_column(sa.String(26), primary_key=True)

    status: Mapped[OrderStatus] = mapped_column(
        EnumStringType(OrderStatus), nullable=False, default=OrderStatus.confirmed
    )
    total: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    # Admin-editable label, defaults to the order ID
    label: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined"
    )

    @property
    def display_label(self) -> str:
        """Return label if set, otherwise return the order ID."""
        return self.label if self.label else self.id


class OrderItem(ModelWithId, ModelWithDates):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(sa.String(26), sa.ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(sa.BigInteger(), sa.ForeignKey("products.id"), nullable=False)
    variation_id: Mapped[int | None] = mapped_column(
        sa.BigInteger(), sa.ForeignKey("product_variations.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(sa.Integer(), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", lazy="joined")
    variation: Mapped["ProductVariation | None"] = relationship("ProductVariation", lazy="joined")
