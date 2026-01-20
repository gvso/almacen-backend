from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId

if TYPE_CHECKING:
    from app.models.product import Product


class Tag(ModelWithId, ModelWithDates):
    __tablename__ = "tags"

    label: Mapped[str] = mapped_column(sa.String(100), nullable=False, unique=True)
    order: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0")

    translations: Mapped[list["TagTranslation"]] = relationship(
        "TagTranslation", back_populates="tag", lazy="selectin", cascade="all, delete-orphan"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", secondary="product_tags", back_populates="tags", lazy="selectin"
    )

    def get_translation(self, language: str | None) -> "TagTranslation | None":
        """Get translation for a specific language."""
        if not language:
            return None
        for translation in self.translations:
            if translation.language == language:
                return translation
        return None

    def to_dict_with_language(self, language: str | None = None) -> dict:
        """Convert to dict, using translated label if available."""
        data = self.as_dict()
        translation = self.get_translation(language)
        if translation:
            data["label"] = translation.label
        return data


class TagTranslation(ModelWithId):
    __tablename__ = "tag_translations"

    tag_id: Mapped[int] = mapped_column(sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    language: Mapped[str] = mapped_column(sa.String(5), nullable=False)
    label: Mapped[str] = mapped_column(sa.String(100), nullable=False)

    tag: Mapped["Tag"] = relationship("Tag", back_populates="translations")

    __table_args__ = (
        sa.UniqueConstraint("tag_id", "language", name="uq_tag_translation_language"),
        sa.Index("ix_tag_translations_tag_language", "tag_id", "language"),
    )


class ProductTag(ModelWithId):
    """Junction table for many-to-many relationship between products and tags."""

    __tablename__ = "product_tags"

    product_id: Mapped[int] = mapped_column(sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    tag_id: Mapped[int] = mapped_column(sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("product_id", "tag_id", name="uq_product_tag"),
        sa.Index("ix_product_tags_product", "product_id"),
        sa.Index("ix_product_tags_tag", "tag_id"),
    )
