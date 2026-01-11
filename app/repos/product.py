from sqlalchemy import func, or_
from sqlalchemy.orm import Query

from app.models import Product
from app.models.product import ProductTranslation
from app.repos.base import Repo


class ProductRepo(Repo[Product]):
    def __init__(self) -> None:
        super().__init__(Product)

    def get_all_active(self) -> Query[Product]:
        return self.get_query().filter(Product.is_active.is_(True)).order_by(Product.order, Product.inserted_at)

    def get_by_ids(self, product_ids: list[int]) -> list[Product]:
        return self.get_query().filter(Product.id.in_(product_ids)).all()

    def filter_by_search(
        self, query: Query[Product], search_term: str, language: str | None = None
    ) -> Query[Product]:
        """Filter products by search term in name or translations."""
        # Join with translations to search in translated names
        query = query.outerjoin(ProductTranslation, Product.id == ProductTranslation.product_id)

        # Build search conditions
        conditions = [func.lower(Product.name).like(search_term)]

        if language:
            # Search only in the specified language translation
            conditions.append(
                (ProductTranslation.language == language) & func.lower(ProductTranslation.name).like(search_term)
            )
        else:
            # Search in any translation
            conditions.append(func.lower(ProductTranslation.name).like(search_term))

        return query.filter(or_(*conditions)).distinct()
