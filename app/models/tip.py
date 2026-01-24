import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ModelWithDates, ModelWithId


class Tip(ModelWithId, ModelWithDates):
    """Tips for Paraguay street culture - small cards with images and descriptions."""

    __tablename__ = "tips"

    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    order: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default="true")

    translations: Mapped[list["TipTranslation"]] = relationship(
        "TipTranslation", back_populates="tip", lazy="selectin", cascade="all, delete-orphan"
    )

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
            data["title"] = translation.title
            data["description"] = translation.description
        return data


class TipTranslation(ModelWithId):
    __tablename__ = "tip_translations"

    tip_id: Mapped[int] = mapped_column(sa.ForeignKey("tips.id", ondelete="CASCADE"), nullable=False)
    language: Mapped[str] = mapped_column(sa.String(5), nullable=False)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text(), nullable=False)

    tip: Mapped["Tip"] = relationship("Tip", back_populates="translations")

    __table_args__ = (
        sa.UniqueConstraint("tip_id", "language", name="uq_tip_translation_language"),
        sa.Index("ix_tip_translations_tip_language", "tip_id", "language"),
    )
