"""add_product_translation

Revision ID: e20738e259f9
Revises: 473c407d4b66
Create Date: 2026-01-10 20:42:40.872506

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e20738e259f9"
down_revision: str | None = "473c407d4b66"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "product_translations",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "language", name="uq_product_translation_language"),
    )
    with op.batch_alter_table("product_translations", schema=None) as batch_op:
        batch_op.create_index("ix_product_translations_product_language", ["product_id", "language"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("product_translations", schema=None) as batch_op:
        batch_op.drop_index("ix_product_translations_product_language")

    op.drop_table("product_translations")
