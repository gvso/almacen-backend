"""Add label to orders

Revision ID: a1b2c3d4e5f6
Revises: 3fe57586e84a
Create Date: 2026-01-11 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "3fe57586e84a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("label", sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "label")
