"""Add category field to tags

Revision ID: add_tag_category
Revises: 20260124_130000_migrate_product_tags_to_entity_tags
Create Date: 2026-01-24 14:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6a7b8c9d0e2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add category column with default 'product' for existing tags
    op.add_column(
        "tags",
        sa.Column("category", sa.String(50), nullable=False, server_default="product"),
    )


def downgrade() -> None:
    op.drop_column("tags", "category")
