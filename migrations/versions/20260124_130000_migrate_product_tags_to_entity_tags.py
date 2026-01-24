"""Migrate product_tags to entity_tags

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-01-24 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f6a7b8c9d0e1"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create new entity_tags table
    op.create_table(
        "entity_tags",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("tag_id", sa.BigInteger(), sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("entity_type", "entity_id", "tag_id", name="uq_entity_tag"),
        sa.Index("ix_entity_tags_entity", "entity_type", "entity_id"),
        sa.Index("ix_entity_tags_tag", "tag_id"),
    )

    # Migrate existing product_tags data to entity_tags with entity_type='product'
    op.execute("""
        INSERT INTO entity_tags (entity_type, entity_id, tag_id)
        SELECT 'product', product_id, tag_id FROM product_tags
    """)

    # Drop old product_tags table
    op.drop_table("product_tags")


def downgrade() -> None:
    # Recreate product_tags table
    op.create_table(
        "product_tags",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("product_id", sa.BigInteger(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag_id", sa.BigInteger(), sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("product_id", "tag_id", name="uq_product_tag"),
        sa.Index("ix_product_tags_product", "product_id"),
        sa.Index("ix_product_tags_tag", "tag_id"),
    )

    # Migrate product entity_tags back to product_tags
    op.execute("""
        INSERT INTO product_tags (product_id, tag_id)
        SELECT entity_id, tag_id FROM entity_tags WHERE entity_type = 'product'
    """)

    # Drop entity_tags table
    op.drop_table("entity_tags")
