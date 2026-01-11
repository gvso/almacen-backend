from pydantic import BaseModel


class CartPath(BaseModel):
    token: str


class CartItemIdPath(BaseModel):
    token: str
    item_id: int


class AddItemRequest(BaseModel):
    product_id: int
    variation_id: int | None = None
    quantity: int = 1


class UpdateItemRequest(BaseModel):
    quantity: int
