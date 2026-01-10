from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import ModelWithDates, ModelWithId


class Product(ModelWithId, ModelWithDates):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default="true")
