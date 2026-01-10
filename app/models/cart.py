from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId

if TYPE_CHECKING:
    from app.models.product import Product


class Cart(ModelWithId, ModelWithDates):
    """Cart identified by a token (ULID) for anonymous users."""

    __tablename__ = "carts"

    token: Mapped[str] = mapped_column(sa.String(26), nullable=False, unique=True, index=True)

    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan", lazy="joined"
    )


class CartItem(ModelWithId, ModelWithDates):
    __tablename__ = "cart_items"

    cart_id: Mapped[int] = mapped_column(sa.BigInteger(), sa.ForeignKey("carts.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(sa.BigInteger(), sa.ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer(), nullable=False, default=1)

    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["Product"] = relationship("Product", lazy="joined")

    __table_args__ = (sa.UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),)
