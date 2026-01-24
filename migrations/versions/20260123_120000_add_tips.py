"""Add tips and tip_translations tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-01-23 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create tips table
    op.create_table(
        "tips",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # Create tip_translations table
    op.create_table(
        "tip_translations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("tip_id", sa.BigInteger(), sa.ForeignKey("tips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language", sa.String(5), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.UniqueConstraint("tip_id", "language", name="uq_tip_translation_language"),
        sa.Index("ix_tip_translations_tip_language", "tip_id", "language"),
    )


def downgrade() -> None:
    op.drop_table("tip_translations")
    op.drop_table("tips")
