from http import HTTPStatus

import flask
from dependency_injector.wiring import Provide, inject
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3.models.tag import Tag as OpenApiTag
from pydantic import BaseModel

from app.container import ApplicationContainer
from app.models.product import ProductType
from app.models.tip import TipType
from app.repos import TagRepo

tags_bp = APIBlueprint("tags", __name__, abp_tags=[OpenApiTag(name="tags")], url_prefix="/api/v1/tags")


class TagsQuery(BaseModel):
    language: str | None = None
    type: ProductType | None = None
    tip_type: TipType | None = None


@tags_bp.get("")
@inject
def list_tags(
    query: TagsQuery,
    tag_repo: TagRepo = Provide[ApplicationContainer.repos.tag],
) -> tuple[flask.Response, HTTPStatus]:
    """Get all tags, optionally filtered by product type or tip type."""
    if query.type:
        tags = tag_repo.get_tags_with_products_by_type(query.type)
    elif query.tip_type:
        tags = tag_repo.get_tags_with_tips_by_type(query.tip_type)
    else:
        tags = tag_repo.get_all().all()

    data = [tag.to_dict_with_language(query.language) for tag in tags]
    return flask.jsonify({"data": data}), HTTPStatus.OK
