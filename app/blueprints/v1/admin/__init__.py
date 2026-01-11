from .auth import auth_bp as admin_auth_bp
from .products import products_bp as admin_products_bp

__all__ = ["admin_auth_bp", "admin_products_bp"]
