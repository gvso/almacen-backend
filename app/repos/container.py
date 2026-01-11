from dependency_injector import containers, providers

from app.repos import CartItemRepo, CartRepo, OrderRepo, ProductRepo, ProductVariationRepo


class RepoContainer(containers.DeclarativeContainer):
    product = providers.Singleton(ProductRepo)
    product_variation = providers.Singleton(ProductVariationRepo)
    cart = providers.Singleton(CartRepo)
    cart_item = providers.Singleton(CartItemRepo)
    order = providers.Singleton(OrderRepo)
