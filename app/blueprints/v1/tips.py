from http import HTTPStatus
from typing import Any

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag

from app.blueprints.v1.models import TipQuery
from app.container import ApplicationContainer
from app.repos.tip import TipRepo

tips_bp = APIBlueprint("tips", __name__, abp_tags=[Tag(name="tips")], url_prefix="/api/v1/tips")


@tips_bp.get("")
@inject
def list_tips(
    query: TipQuery,
    tip_repo: TipRepo = Provide[ApplicationContainer.repos.tip],
) -> tuple[flask.Response, HTTPStatus]:
    """Get all active tips."""
    tips = tip_repo.get_all_active().all()
    data: list[dict[str, Any]] = [tip.to_dict_with_language(query.language) for tip in tips]
    return flask.jsonify({"data": data}), HTTPStatus.OK
