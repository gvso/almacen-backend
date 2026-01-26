from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId


class EntityType(str, Enum):
    product = "product"
    tip = "tip"


class TagCategory(str, Enum):
    product = "product"
    tip = "tip"


class Tag(ModelWithId, ModelWithDates):
    __tablename__ = "tags"

    label: Mapped[str] = mapped_column(sa.String(100), nullable=False, unique=True)
    category: Mapped[TagCategory] = mapped_column(
        sa.Enum(TagCategory, name="tag_category", native_enum=False),
        nullable=False,
        server_default=TagCategory.product.value,
    )
    order: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0")
    is_filterable: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default="true")
    bg_color: Mapped[str] = mapped_column(sa.String(7), nullable=False, server_default="#f5f5f4")
    text_color: Mapped[str] = mapped_column(sa.String(7), nullable=False, server_default="#57534e")

    translations: Mapped[list["TagTranslation"]] = relationship(
        "TagTranslation", back_populates="tag", lazy="selectin", cascade="all, delete-orphan"
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
        """Convert to dict, using translated label if available.

        Includes 'key' field with the original/base label for URL matching.
        """
        data = self.as_dict()
        data["key"] = self.label  # Original label for URL matching
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


class EntityTag(ModelWithId):
    """Junction table for many-to-many relationship between entities (products, tips) and tags."""

    __tablename__ = "entity_tags"

    entity_type: Mapped[EntityType] = mapped_column(
        sa.Enum(EntityType, name="entity_type", native_enum=False),
        nullable=False,
    )
    entity_id: Mapped[int] = mapped_column(sa.BigInteger(), nullable=False)
    tag_id: Mapped[int] = mapped_column(sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    tag: Mapped["Tag"] = relationship("Tag", lazy="selectin")

    __table_args__ = (
        sa.UniqueConstraint("entity_type", "entity_id", "tag_id", name="uq_entity_tag"),
        sa.Index("ix_entity_tags_entity", "entity_type", "entity_id"),
        sa.Index("ix_entity_tags_tag", "tag_id"),
    )


# Keep ProductTag as an alias for backward compatibility during migration
ProductTag = EntityTag
