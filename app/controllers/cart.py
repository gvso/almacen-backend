from ulid import ULID

from app.exceptions import EntityNotFoundError, InvalidDataError
from app.models import Cart, CartItem
from app.repos import CartItemRepo, CartRepo, ProductRepo


class CartController:
    def __init__(
        self,
        cart_repo: CartRepo,
        cart_item_repo: CartItemRepo,
        product_repo: ProductRepo,
    ) -> None:
        self._cart_repo = cart_repo
        self._cart_item_repo = cart_item_repo
        self._product_repo = product_repo

    def get_or_create_cart(self, token: str | None) -> Cart:
        """Get existing cart by token or create a new one."""
        if token:
            cart = self._cart_repo.get_by_token(token)
            if cart:
                return cart

        # Create new cart with ULID token
        new_token = str(ULID())
        cart = Cart(token=new_token)
        return self._cart_repo.persist(cart)

    def get_cart(self, token: str) -> Cart:
        """Get cart by token or raise error."""
        cart = self._cart_repo.get_by_token(token)
        if not cart:
            raise EntityNotFoundError(f"Cart with token {token} not found")
        return cart

    def add_item(self, token: str, product_id: int, quantity: int = 1) -> Cart:
        """Add a product to the cart."""
        if quantity < 1:
            raise InvalidDataError("Quantity must be at least 1")

        cart = self.get_or_create_cart(token)
        product = self._product_repo.get(str(product_id))

        if not product or not product.is_active:
            raise EntityNotFoundError(f"Product with id {product_id} not found")

        # Check if item already exists in cart
        existing_item = self._cart_item_repo.get_by_cart_and_product(cart.id, product_id)

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            self._cart_item_repo.update(existing_item, {"quantity": new_quantity})
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            self._cart_item_repo.persist(cart_item)

        # Refresh cart to get updated items
        return self.get_cart(cart.token)

    def update_item_quantity(self, token: str, product_id: int, quantity: int) -> Cart:
        """Update the quantity of an item in the cart."""
        cart = self.get_cart(token)

        existing_item = self._cart_item_repo.get_by_cart_and_product(cart.id, product_id)
        if not existing_item:
            raise EntityNotFoundError(f"Product {product_id} not in cart")

        if quantity < 1:
            # Remove item if quantity is 0 or less
            self._cart_item_repo.remove(existing_item, hard_delete=True)
        else:
            self._cart_item_repo.update(existing_item, {"quantity": quantity})

        return self.get_cart(token)

    def remove_item(self, token: str, product_id: int) -> Cart:
        """Remove an item from the cart."""
        cart = self.get_cart(token)

        existing_item = self._cart_item_repo.get_by_cart_and_product(cart.id, product_id)
        if not existing_item:
            raise EntityNotFoundError(f"Product {product_id} not in cart")

        self._cart_item_repo.remove(existing_item, hard_delete=True)
        return self.get_cart(token)

    def clear_cart(self, token: str) -> None:
        """Remove the cart and all its items."""
        cart = self.get_cart(token)
        # Deleting the cart will cascade delete all items due to relationship config
        self._cart_repo.remove(cart, hard_delete=True)
