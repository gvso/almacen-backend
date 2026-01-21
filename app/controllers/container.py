from typing import cast

from dependency_injector import containers, providers

from app.controllers.cart import CartController
from app.controllers.order import OrderController
from app.controllers.product import ProductController
from app.repos.container import RepoContainer


class ControllerContainer(containers.DeclarativeContainer):
    repos = cast(RepoContainer, providers.DependenciesContainer())

    cart = providers.Singleton(
        CartController,
        cart_repo=repos.cart,
        cart_item_repo=repos.cart_item,
        product_repo=repos.product,
        product_variation_repo=repos.product_variation,
    )

    order = providers.Singleton(
        OrderController,
        order_repo=repos.order,
        cart_controller=cart,
    )

    product = providers.Singleton(
        ProductController,
        product_repo=repos.product,
    )
