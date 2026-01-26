"""Add is_filterable, bg_color, and text_color fields to tags

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e2
Create Date: 2026-01-26 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "g7h8i9j0k1l2"
down_revision = "f6a7b8c9d0e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_filterable column with default True for existing tags
    op.add_column(
        "tags",
        sa.Column("is_filterable", sa.Boolean(), nullable=False, server_default="true"),
    )
    # Add bg_color column with default stone-100 color
    op.add_column(
        "tags",
        sa.Column("bg_color", sa.String(7), nullable=False, server_default="#f5f5f4"),
    )
    # Add text_color column with default stone-600 color
    op.add_column(
        "tags",
        sa.Column("text_color", sa.String(7), nullable=False, server_default="#57534e"),
    )


def downgrade() -> None:
    op.drop_column("tags", "text_color")
    op.drop_column("tags", "bg_color")
    op.drop_column("tags", "is_filterable")
