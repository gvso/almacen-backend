from .admin import (
    admin_auth_bp,
    admin_documents_bp,
    admin_orders_bp,
    admin_products_bp,
    admin_tags_bp,
    admin_tips_bp,
)
from .cart import cart_bp
from .health import health_bp
from .orders import orders_bp
from .products import products_bp
from .tags import tags_bp
from .tips import tips_bp

__all__ = [
    "admin_auth_bp",
    "admin_documents_bp",
    "admin_orders_bp",
    "admin_products_bp",
    "admin_tags_bp",
    "admin_tips_bp",
    "cart_bp",
    "health_bp",
    "orders_bp",
    "products_bp",
    "tags_bp",
    "tips_bp",
]
