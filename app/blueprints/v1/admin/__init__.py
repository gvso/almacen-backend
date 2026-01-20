from .auth import auth_bp as admin_auth_bp
from .documents import documents_bp as admin_documents_bp
from .orders import orders_bp as admin_orders_bp
from .products import products_bp as admin_products_bp
from .tags import tags_bp as admin_tags_bp

__all__ = ["admin_auth_bp", "admin_documents_bp", "admin_orders_bp", "admin_products_bp", "admin_tags_bp"]
