from pydantic import BaseModel

from app.models.product import ProductType


class ProductQuery(BaseModel):
    language: str | None = None
    search: str | None = None
    type: ProductType | None = None


class ProductPath(BaseModel):
    product_id: int
