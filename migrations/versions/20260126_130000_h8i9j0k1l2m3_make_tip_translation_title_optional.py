"""Make tip translation title optional

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-01-26 13:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make title column nullable in tip_translations
    op.alter_column(
        "tip_translations",
        "title",
        existing_type=sa.String(255),
        nullable=True,
    )


def downgrade() -> None:
    # Make title column non-nullable in tip_translations
    # Note: This will fail if there are NULL values
    op.alter_column(
        "tip_translations",
        "title",
        existing_type=sa.String(255),
        nullable=False,
    )
