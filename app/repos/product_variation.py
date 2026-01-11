from app.models import ProductVariation
from app.repos.base import Repo


class ProductVariationRepo(Repo[ProductVariation]):
    def __init__(self) -> None:
        super().__init__(ProductVariation)

    def get_by_product_id(self, product_id: int) -> list[ProductVariation]:
        return (
            self.get_query()
            .filter(ProductVariation.product_id == product_id, ProductVariation.is_active.is_(True))
            .all()
        )
