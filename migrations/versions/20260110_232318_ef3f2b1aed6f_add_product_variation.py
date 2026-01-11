"""add_product_variation

Revision ID: ef3f2b1aed6f
Revises: e20738e259f9
Create Date: 2026-01-10 23:23:18.511599

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ef3f2b1aed6f"
down_revision: str | None = "e20738e259f9"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "product_variations",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "product_variation_translations",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("variation_id", sa.BigInteger(), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["variation_id"], ["product_variations.id"]),
        sa.UniqueConstraint("variation_id", "language", name="uq_product_variation_translation_language"),
    )
    with op.batch_alter_table("product_variation_translations", schema=None) as batch_op:
        batch_op.create_index(
            "ix_product_variation_translations_variation_language", ["variation_id", "language"], unique=False
        )

    with op.batch_alter_table("cart_items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("variation_id", sa.BigInteger(), nullable=True))
        batch_op.drop_constraint(batch_op.f("uq_cart_product"), type_="unique")
        batch_op.create_unique_constraint("uq_cart_product_variation", ["cart_id", "product_id", "variation_id"])
        batch_op.create_foreign_key(None, "product_variations", ["variation_id"], ["id"])

    with op.batch_alter_table("order_items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("variation_id", sa.BigInteger(), nullable=True))
        batch_op.create_foreign_key(None, "product_variations", ["variation_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("order_items", schema=None) as batch_op:
        batch_op.drop_constraint("order_items_variation_id_fkey", type_="foreignkey")
        batch_op.drop_column("variation_id")

    with op.batch_alter_table("cart_items", schema=None) as batch_op:
        batch_op.drop_constraint("cart_items_variation_id_fkey", type_="foreignkey")
        batch_op.drop_constraint("uq_cart_product_variation", type_="unique")
        batch_op.create_unique_constraint(
            batch_op.f("uq_cart_product"), ["cart_id", "product_id"], postgresql_nulls_not_distinct=False
        )
        batch_op.drop_column("variation_id")

    with op.batch_alter_table("product_variation_translations", schema=None) as batch_op:
        batch_op.drop_index("ix_product_variation_translations_variation_language")

    op.drop_table("product_variation_translations")
    op.drop_table("product_variations")
