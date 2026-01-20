from pydantic import BaseModel, Field

from app.models.product import ProductType


class ProductQuery(BaseModel):
    language: str | None = None
    search: str | None = None
    type: ProductType | None = None
    tag_ids: str | None = Field(None, description="Comma-separated list of tag IDs to filter by")


class ProductPath(BaseModel):
    product_id: int
