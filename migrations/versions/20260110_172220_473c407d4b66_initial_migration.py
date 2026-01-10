"""initial_migration

Revision ID: 473c407d4b66
Revises:
Create Date: 2026-01-10 17:22:20.011667

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "473c407d4b66"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "carts",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("token", sa.String(length=26), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("carts", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_carts_token"), ["token"], unique=True)

    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("total", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cart_items",
        sa.PrimaryKeyConstraint("id"),
        sa.Column("cart_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("inserted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("order_id", sa.String(length=26), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("cart_items")
    op.drop_table("products")
    op.drop_table("orders")
    with op.batch_alter_table("carts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_carts_token"))

    op.drop_table("carts")
