from dependency_injector import containers, providers

from app.repos import (
    CartItemRepo,
    CartRepo,
    EntityTagRepo,
    OrderRepo,
    ProductRepo,
    ProductVariationRepo,
    TagRepo,
    TipRepo,
)


class RepoContainer(containers.DeclarativeContainer):
    product = providers.Singleton(ProductRepo)
    product_variation = providers.Singleton(ProductVariationRepo)
    cart = providers.Singleton(CartRepo)
    cart_item = providers.Singleton(CartItemRepo)
    order = providers.Singleton(OrderRepo)
    tag = providers.Singleton(TagRepo)
    tip = providers.Singleton(TipRepo)
    entity_tag = providers.Singleton(EntityTagRepo)
