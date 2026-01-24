from sqlalchemy.orm import Query

from app.models.tip import Tip, TipType
from app.repos.base import Repo


class TipRepo(Repo[Tip]):
    def __init__(self) -> None:
        super().__init__(Tip)

    def get_all_active(self, tip_type: str | None = None) -> Query[Tip]:
        """Get all active tips ordered by order, then inserted_at.

        Args:
            tip_type: Optional filter by tip type ('quick_tip' or 'business')
        """
        query = self.get_query().filter(Tip.is_active.is_(True))
        if tip_type:
            query = query.filter(Tip.tip_type == TipType(tip_type))
        return query.order_by(Tip.order, Tip.inserted_at)

    def get_all(self) -> Query[Tip]:
        """Get all tips ordered by order, then inserted_at (for admin)."""
        return self.get_query().order_by(Tip.order, Tip.inserted_at)

    def get_max_order(self) -> int:
        """Get the maximum order value among all tips."""
        from sqlalchemy import func

        result = self.session.query(func.max(Tip.order)).scalar()
        return result if result is not None else -1
