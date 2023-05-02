from typing import List, Tuple

from app.models.order import OrderOrm
from app.models.pageable import PageRequestSchema
from app.repository.order_repository import OrderRepository


class OrderService:
    def __init__(self):
        self.order_repo: OrderRepository = OrderRepository()

    def create_order(self, order: OrderOrm) -> OrderOrm:
        return self.order_repo.save(order)

    def get_order(self, order_id: str) -> OrderOrm:
        return self.order_repo.get_by_id(order_id)

    def get_order_by_address_id(self, address_id: str) -> OrderOrm:
        return self.order_repo.get_by_address_id(address_id)

    def update_order(self, order_id: str, updated_order: OrderOrm):
        order: OrderOrm = self.order_repo.get_by_id(order_id)
        order.name = updated_order.name
        order.price = updated_order.price
        return self.order_repo.save(order)

    def get_paged_orders(self, pageable: PageRequestSchema) -> Tuple[List, int]:
        return self.order_repo.get_paged_items(pageable, {})
