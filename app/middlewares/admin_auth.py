from functools import wraps
from http import HTTPStatus
from typing import Any, Callable

import flask
import jwt

from app_settings import settings

JWT_ALGORITHM = "HS256"


def require_admin_auth(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require admin JWT authentication for a route."""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        auth_header = flask.request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return (
                flask.jsonify({"error": "unauthorized", "error_description": "Missing or invalid token"}),
                HTTPStatus.UNAUTHORIZED,
            )

        token = auth_header[7:]  # Remove "Bearer " prefix

        try:
            jwt.decode(token, settings.session_key, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return (
                flask.jsonify({"error": "unauthorized", "error_description": "Token has expired"}),
                HTTPStatus.UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            return (
                flask.jsonify({"error": "unauthorized", "error_description": "Invalid token"}),
                HTTPStatus.UNAUTHORIZED,
            )

        return f(*args, **kwargs)

    return decorated_function
