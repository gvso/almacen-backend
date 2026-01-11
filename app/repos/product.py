from sqlalchemy.orm import Query

from app.models import Product
from app.repos.base import Repo


class ProductRepo(Repo[Product]):
    def __init__(self) -> None:
        super().__init__(Product)

    def get_all_active(self) -> Query[Product]:
        return self.get_query().filter(Product.is_active.is_(True)).order_by(Product.order, Product.inserted_at)

    def get_by_ids(self, product_ids: list[int]) -> list[Product]:
        return self.get_query().filter(Product.id.in_(product_ids)).all()
