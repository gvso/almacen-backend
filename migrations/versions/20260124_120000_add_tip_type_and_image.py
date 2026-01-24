"""Add tip_type and image_url columns to tips

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-01-24 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add image_url column
    op.add_column(
        "tips",
        sa.Column("image_url", sa.String(500), nullable=True),
    )
    # Add tip_type column with default 'quick_tip' for existing rows
    op.add_column(
        "tips",
        sa.Column("tip_type", sa.String(20), nullable=False, server_default="quick_tip"),
    )


def downgrade() -> None:
    op.drop_column("tips", "tip_type")
    op.drop_column("tips", "image_url")
