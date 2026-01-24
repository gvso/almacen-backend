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
    """Get all active tips, optionally filtered by tip_type and tags."""
    tips_query = tip_repo.get_all_active(tip_type=query.tip_type)

    if query.tag_ids:
        tag_id_list = [int(tid.strip()) for tid in query.tag_ids.split(",") if tid.strip().isdigit()]
        if tag_id_list:
            tips_query = tip_repo.filter_by_tags(tips_query, tag_id_list)

    tips = tips_query.all()
    data: list[dict[str, Any]] = [tip.to_dict_with_language(query.language) for tip in tips]
    return flask.jsonify({"data": data}), HTTPStatus.OK
