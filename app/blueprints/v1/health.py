from http import HTTPStatus

import flask
from flask_openapi3.blueprint import APIBlueprint, Tag

health_bp = APIBlueprint("health", __name__, abp_tags=[Tag(name="health")], url_prefix="/api/v1/health")


@health_bp.get("")
def ping() -> tuple[flask.Response, HTTPStatus]:
    return flask.jsonify({"status": "success"}), HTTPStatus.OK
