from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import ColumnElement

from app.models import Product
from app.models.product import ProductTranslation, ProductType
from app.repos.base import Repo


class ProductRepo(Repo[Product]):
    def __init__(self) -> None:
        super().__init__(Product)

    def get_all_active(self, product_type: ProductType | None = None) -> Query[Product]:
        query = self.get_query().filter(Product.is_active.is_(True))
        if product_type:
            query = query.filter(Product.type == product_type)
        return query.order_by(Product.order, Product.inserted_at)

    def filter_by_type(self, query: Query[Product], product_type: ProductType) -> Query[Product]:
        """Filter products by type."""
        return query.filter(Product.type == product_type)

    def get_by_ids(self, product_ids: list[int]) -> list[Product]:
        return self.get_query().filter(Product.id.in_(product_ids)).all()

    def filter_by_search(self, query: Query[Product], search_term: str, language: str | None = None) -> Query[Product]:
        """Filter products by search term in name or translations."""
        # Join with translations to search in translated names
        query = query.outerjoin(ProductTranslation, Product.id == ProductTranslation.product_id)

        # Build search conditions
        conditions: list[ColumnElement[bool]] = [func.lower(Product.name).like(search_term)]

        if language:
            # Search only in the specified language translation
            conditions.append(
                and_(ProductTranslation.language == language, func.lower(ProductTranslation.name).like(search_term))
            )
        else:
            # Search in any translation
            conditions.append(func.lower(ProductTranslation.name).like(search_term))

        return query.filter(or_(*conditions)).distinct()
