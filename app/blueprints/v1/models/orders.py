from pydantic import BaseModel


class OrderPath(BaseModel):
    order_id: str


class CheckoutRequest(BaseModel):
    cart_token: str
    contact_info: str | None = None
    notes: str | None = None
