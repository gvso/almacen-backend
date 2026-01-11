"""add_order_to_products

Revision ID: 3fe57586e84a
Revises: ef3f2b1aed6f
Create Date: 2026-01-10 23:50:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3fe57586e84a"
down_revision: str | None = "ef3f2b1aed6f"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("order", sa.Integer(), server_default="0", nullable=False))


def downgrade() -> None:
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("order")
