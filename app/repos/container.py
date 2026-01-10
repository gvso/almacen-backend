from dependency_injector import containers, providers

from app.repos import CartItemRepo, CartRepo, OrderRepo, ProductRepo


class RepoContainer(containers.DeclarativeContainer):
    product = providers.Singleton(ProductRepo)
    cart = providers.Singleton(CartRepo)
    cart_item = providers.Singleton(CartItemRepo)
    order = providers.Singleton(OrderRepo)
