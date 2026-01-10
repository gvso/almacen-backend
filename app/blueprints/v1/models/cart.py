from pydantic import BaseModel


class CartPath(BaseModel):
    token: str


class CartItemPath(BaseModel):
    token: str
    product_id: int


class AddItemRequest(BaseModel):
    product_id: int
    quantity: int = 1


class UpdateItemRequest(BaseModel):
    quantity: int
