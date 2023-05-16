from typing import List, Tuple

from app.models.order import OrderOrm
from app.models.pageable import PageRequestSchema
from app.repository.order_repository import OrderRepository


class OrderService:
    def __init__(self):
        self.order_repo: OrderRepository = OrderRepository()

    async def create_order(self, order: OrderOrm) -> OrderOrm:
        return await self.order_repo.save(order)

    async def get_order(self, order_id: int) -> OrderOrm:
        return await self.order_repo.get_by_id(order_id)

    async def get_order_by_address_id(self, address_id: int) -> OrderOrm:
        return await self.order_repo.get_by_address_id(address_id)

    async def update_order(self, order_id: int, updated_order: OrderOrm):
        order: OrderOrm = await self.order_repo.get_by_id(order_id)
        order.name = updated_order.name
        order.price = updated_order.price
        return await self.order_repo.save(order)

    async def delete_order(self, order_id: int):
        return await self.order_repo.delete_by_id(order_id)

    async def get_paged_orders(self, pageable: PageRequestSchema) -> Tuple[List, int]:
        return await self.order_repo.get_paged_items(pageable, {})
