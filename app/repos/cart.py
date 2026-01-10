from app.models import Cart, CartItem
from app.repos.base import Repo


class CartRepo(Repo[Cart]):
    def __init__(self) -> None:
        super().__init__(Cart)

    def get_by_token(self, token: str) -> Cart | None:
        return self.get_query().filter(Cart.token == token).first()


class CartItemRepo(Repo[CartItem]):
    def __init__(self) -> None:
        super().__init__(CartItem)

    def get_by_cart_and_product(self, cart_id: int, product_id: int) -> CartItem | None:
        return (
            self.get_query()
            .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .first()
        )
