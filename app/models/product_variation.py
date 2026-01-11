from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId

if TYPE_CHECKING:
    from app.models.product import Product


class ProductVariation(ModelWithId, ModelWithDates):
    __tablename__ = "product_variations"

    product_id: Mapped[int] = mapped_column(sa.ForeignKey("products.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    price: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 2), nullable=True)
    image_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    order: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default="true")

    product: Mapped["Product"] = relationship("Product", back_populates="variations")
    translations: Mapped[list["ProductVariationTranslation"]] = relationship(
        "ProductVariationTranslation", back_populates="variation", lazy="selectin"
    )

    def get_translation(self, language: str | None) -> "ProductVariationTranslation | None":
        """Get translation for a specific language."""
        if not language:
            return None
        for translation in self.translations:
            if translation.language == language:
                return translation
        return None

    def to_dict_with_language(self, language: str | None = None) -> dict:
        """Convert to dict, using translated name if available."""
        data = self.as_dict()
        translation = self.get_translation(language)
        if translation:
            data["name"] = translation.name
        return data


class ProductVariationTranslation(ModelWithId):
    __tablename__ = "product_variation_translations"

    variation_id: Mapped[int] = mapped_column(sa.ForeignKey("product_variations.id"), nullable=False)
    language: Mapped[str] = mapped_column(sa.String(5), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    variation: Mapped["ProductVariation"] = relationship("ProductVariation", back_populates="translations")

    __table_args__ = (
        sa.UniqueConstraint("variation_id", "language", name="uq_product_variation_translation_language"),
        sa.Index("ix_product_variation_translations_variation_language", "variation_id", "language"),
    )
