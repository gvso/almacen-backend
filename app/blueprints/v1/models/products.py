from pydantic import BaseModel


class ProductQuery(BaseModel):
    language: str | None = None
    search: str | None = None


class ProductPath(BaseModel):
    product_id: int
