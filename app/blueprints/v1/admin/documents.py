from http import HTTPStatus

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.container import ApplicationContainer
from app.middlewares.admin_auth import require_admin_auth
from app.services import CloudStorageService

from .models import ImageUploadRequest

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

documents_bp = APIBlueprint(
    "admin_documents",
    __name__,
    abp_tags=[Tag(name="admin-documents")],
    url_prefix="/api/v1/admin/documents",
)


@documents_bp.post("/images/signed-url")
@require_admin_auth
@inject
def get_signed_upload_url(
    body: ImageUploadRequest,
    cloud_storage: CloudStorageService = Provide[ApplicationContainer.services.cloud_storage],
) -> tuple[flask.Response, HTTPStatus]:
    """
    Get a signed URL for uploading an image directly to Cloud Storage.

    The frontend should:
    1. Call this endpoint with the content_type of the image
    2. Use the returned upload_url to PUT the image directly to GCS
    3. Use the public_url when creating/updating the product
    """
    if body.content_type not in ALLOWED_IMAGE_TYPES:
        return (
            flask.jsonify({"error": "bad_request", "error_description": f"Invalid content type: {body.content_type}"}),
            HTTPStatus.BAD_REQUEST,
        )

    result = cloud_storage.generate_signed_upload_url(body.content_type)
    return flask.jsonify(result), HTTPStatus.OK
