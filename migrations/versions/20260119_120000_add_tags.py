"""Add tags, tag_translations, and product_tags tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-01-19 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create tags table
    op.create_table(
        "tags",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("label", sa.String(100), nullable=False, unique=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )

    # Create tag_translations table
    op.create_table(
        "tag_translations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("tag_id", sa.BigInteger(), sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language", sa.String(5), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.UniqueConstraint("tag_id", "language", name="uq_tag_translation_language"),
        sa.Index("ix_tag_translations_tag_language", "tag_id", "language"),
    )

    # Create product_tags junction table
    op.create_table(
        "product_tags",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("product_id", sa.BigInteger(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag_id", sa.BigInteger(), sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("product_id", "tag_id", name="uq_product_tag"),
        sa.Index("ix_product_tags_product", "product_id"),
        sa.Index("ix_product_tags_tag", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("product_tags")
    op.drop_table("tag_translations")
    op.drop_table("tags")
