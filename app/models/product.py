from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId


class Product(ModelWithId, ModelWithDates):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default="true")

    translations: Mapped[list["ProductTranslation"]] = relationship(
        "ProductTranslation", back_populates="product", lazy="selectin"
    )

    def get_translation(self, language: str | None) -> "ProductTranslation | None":
        """Get translation for a specific language."""
        if not language:
            return None
        for translation in self.translations:
            if translation.language == language:
                return translation
        return None

    def to_dict_with_language(self, language: str | None = None) -> dict:
        """Convert to dict, using translated name/description if available."""
        data = self.as_dict()
        translation = self.get_translation(language)
        if translation:
            data["name"] = translation.name
            data["description"] = translation.description
        return data


class ProductTranslation(ModelWithId):
    __tablename__ = "product_translations"

    product_id: Mapped[int] = mapped_column(sa.ForeignKey("products.id"), nullable=False)
    language: Mapped[str] = mapped_column(sa.String(5), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="translations")

    __table_args__ = (
        sa.UniqueConstraint("product_id", "language", name="uq_product_translation_language"),
        sa.Index("ix_product_translations_product_language", "product_id", "language"),
    )
