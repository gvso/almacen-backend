from sqlalchemy.orm import Query

from app.models.product import Product, ProductType
from app.models.tag import ProductTag, Tag
from app.repos.base import Repo


class TagRepo(Repo[Tag]):
    def __init__(self) -> None:
        super().__init__(Tag)

    def get_all(self) -> Query[Tag]:
        """Get all tags ordered by order, then label."""
        return self.get_query().order_by(Tag.order, Tag.label)

    def get_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        """Get tags by their IDs."""
        return self.get_query().filter(Tag.id.in_(tag_ids)).all()

    def get_by_label(self, label: str) -> Tag | None:
        """Get a tag by its label."""
        return self.get_query().filter(Tag.label == label).first()

    def get_tags_with_products_by_type(self, product_type: ProductType) -> list[Tag]:
        """Get tags that have at least one active product of the specified type."""
        return (
            self.get_query()
            .join(ProductTag, Tag.id == ProductTag.tag_id)
            .join(Product, ProductTag.product_id == Product.id)
            .filter(Product.type == product_type, Product.is_active.is_(True))
            .distinct()
            .order_by(Tag.order, Tag.label)
            .all()
        )

    def get_max_order(self) -> int:
        """Get the maximum order value among all tags."""
        from sqlalchemy import func

        result = self.session.query(func.max(Tag.order)).scalar()
        return result if result is not None else -1
