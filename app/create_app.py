import logging
from http import HTTPStatus

from flask import Response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_openapi3.models.info import Info
from flask_openapi3.openapi import OpenAPI
from werkzeug.exceptions import HTTPException

from app.blueprints.v1 import (
    admin_auth_bp,
    admin_documents_bp,
    admin_orders_bp,
    admin_products_bp,
    admin_tags_bp,
    admin_tips_bp,
    cart_bp,
    health_bp,
    orders_bp,
    products_bp,
    tags_bp,
    tips_bp,
)
from app.db import db, reconnect_db
from app.exceptions import BaseError, ErrorType
from app_settings import settings
from environment import Environment


def _register_endpoints(app: OpenAPI) -> None:
    app.register_api(health_bp)
    app.register_api(products_bp)
    app.register_api(tags_bp)
    app.register_api(tips_bp)
    app.register_api(cart_bp)
    app.register_api(orders_bp)
    app.register_api(admin_auth_bp)
    app.register_api(admin_documents_bp)
    app.register_api(admin_orders_bp)
    app.register_api(admin_products_bp)
    app.register_api(admin_tags_bp)
    app.register_api(admin_tips_bp)


def _setup_error_handlers(app: OpenAPI) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException) -> tuple[Response, HTTPStatus]:
        return (
            jsonify({"error": "bad_request"}),
            HTTPStatus(e.code) if e.code else HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(BaseError)
    def handle_app_error(e: BaseError) -> tuple[Response, HTTPStatus]:
        if e.status_code >= 400 and e.status_code < 500:
            app.logger.warning(
                f"A user-related (HTTP 4xx) error occurred; {e}",
                exc_info=True,
                extra=e.extra,
            )
        else:
            app.logger.exception(f"An unhandled app exception occurred; {e}", extra=e.extra)
        return jsonify({"error": e.error_type.value, "error_description": e.message}), e.status_code

    @app.errorhandler(Exception)
    def handle_error(e: Exception) -> tuple[Response, HTTPStatus]:
        if settings.environment == Environment.TEST:
            logging.exception(f"An unhandled exception occurred; error: {e}")
        app.logger.exception(f"An unhandled exception occurred; error: {e}")
        return jsonify({"error": ErrorType.UNHANDLED_EXCEPTION.value}), HTTPStatus.INTERNAL_SERVER_ERROR

    app.register_error_handler(HTTPException, handle_http_error)
    app.register_error_handler(BaseError, handle_app_error)
    app.register_error_handler(Exception, handle_error)


def create_app() -> OpenAPI:
    info = Info(title="Almacen API", version="1.0.0")
    app = OpenAPI(
        __name__,
        info=info,
        doc_ui=settings.environment == Environment.DEVELOPMENT,
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.sqlalchemy.database_url
    app.logger.setLevel(settings.logging.level)
    app.secret_key = settings.session_key

    db.init_app(app)
    Migrate(app, db, compare_type=True)

    _register_endpoints(app)
    _setup_error_handlers(app)
    CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

    @app.after_request
    def after_request(response: Response) -> Response:
        db.session.commit()
        return response

    @app.before_request
    def ensure_db_connection() -> None:
        reconnect_db(db)

    return app
