from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId
from app.models.tag import EntityTag, EntityType, Tag


class TipType(str, Enum):
    quick_tip = "quick_tip"
    business = "business"


class Tip(ModelWithId, ModelWithDates):
    """Tips for Paraguay street culture - small cards with images and descriptions."""

    __tablename__ = "tips"

    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    image_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    order: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default="true")
    tip_type: Mapped[TipType] = mapped_column(
        sa.Enum(TipType, name="tip_type", native_enum=False),
        nullable=False,
        server_default=TipType.quick_tip.name,
    )

    translations: Mapped[list["TipTranslation"]] = relationship(
        "TipTranslation", back_populates="tip", lazy="selectin", cascade="all, delete-orphan"
    )
    _entity_tags: Mapped[list["EntityTag"]] = relationship(
        "EntityTag",
        primaryjoin="and_(Tip.id == foreign(EntityTag.entity_id), EntityTag.entity_type == 'tip')",
        lazy="selectin",
        cascade="all, delete-orphan",
        viewonly=False,
    )

    @property
    def tags(self) -> list["Tag"]:
        """Get all tags for this tip."""
        return [et.tag for et in self._entity_tags]

    @tags.setter
    def tags(self, new_tags: list["Tag"]) -> None:
        """Set tags for this tip by replacing entity_tags."""
        self._entity_tags = [
            EntityTag(entity_type=EntityType.tip, entity_id=self.id, tag_id=tag.id) for tag in new_tags
        ]

    def get_translation(self, language: str | None) -> "TipTranslation | None":
        """Get translation for a specific language."""
        if not language:
            return None
        for translation in self.translations:
            if translation.language == language:
                return translation
        return None

    def to_dict_with_language(self, language: str | None = None) -> dict:
        """Convert to dict, using translated title/description if available."""
        data = self.as_dict()
        translation = self.get_translation(language)
        if translation:
            if translation.title:
                data["title"] = translation.title
            data["description"] = translation.description
        # Include tags with translations
        data["tags"] = [tag.to_dict_with_language(language) for tag in self.tags]
        return data


class TipTranslation(ModelWithId):
    __tablename__ = "tip_translations"

    tip_id: Mapped[int] = mapped_column(sa.ForeignKey("tips.id", ondelete="CASCADE"), nullable=False)
    language: Mapped[str] = mapped_column(sa.String(5), nullable=False)
    title: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    description: Mapped[str] = mapped_column(sa.Text(), nullable=False)

    tip: Mapped["Tip"] = relationship("Tip", back_populates="translations")

    __table_args__ = (
        sa.UniqueConstraint("tip_id", "language", name="uq_tip_translation_language"),
        sa.Index("ix_tip_translations_tip_language", "tip_id", "language"),
    )
