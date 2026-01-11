from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import flask
import jwt
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.middlewares.admin_auth import require_admin_auth
from app_settings import settings

from .models import ErrorResponse, LoginRequest, LoginResponse

auth_bp = APIBlueprint(
    "admin_auth",
    __name__,
    abp_tags=[Tag(name="admin")],
    url_prefix="/api/v1/admin",
)

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_jwt_token() -> str:
    """Create a JWT token for admin session."""
    payload = {
        "sub": "admin",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, settings.session_key, algorithm=JWT_ALGORITHM)


@auth_bp.post(
    "/login",
    responses={
        HTTPStatus.OK: LoginResponse,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
)
def login(body: LoginRequest) -> tuple[flask.Response, HTTPStatus]:
    """Authenticate admin and issue JWT token."""
    if body.password != settings.admin_password:
        return (
            flask.jsonify({"error": "unauthorized", "error_description": "Invalid password"}),
            HTTPStatus.UNAUTHORIZED,
        )

    token = create_jwt_token()
    return flask.jsonify({"token": token}), HTTPStatus.OK


@auth_bp.get(
    "/verify",
    responses={
        HTTPStatus.OK: None,
        HTTPStatus.UNAUTHORIZED: ErrorResponse,
    },
)
@require_admin_auth
def verify() -> tuple[flask.Response, HTTPStatus]:
    """Verify the current admin session is valid."""
    return flask.jsonify({"status": "valid"}), HTTPStatus.OK


@auth_bp.get("/dashboard")
@require_admin_auth
def dashboard() -> tuple[flask.Response, HTTPStatus]:
    """Admin dashboard endpoint - protected by JWT."""
    return flask.jsonify({"message": "Welcome to the admin dashboard"}), HTTPStatus.OK
