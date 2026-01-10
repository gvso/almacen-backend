from app.models import Order
from app.repos.base import Repo


class OrderRepo(Repo[Order]):
    def __init__(self) -> None:
        super().__init__(Order)

    def get_by_ulid(self, ulid: str) -> Order | None:
        return self.get(ulid)
