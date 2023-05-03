from typing import List

from fastapi import Depends, APIRouter
from fastapi_restful.cbv import cbv
from starlette.status import HTTP_201_CREATED

from app.models.order import OrderSchema, OrderOrm
from app.models.pageable import PageRequestSchema, PageResponseSchema
from app.services.order_service import OrderService

order_router = APIRouter()


@cbv(order_router)
class OrderController:
    def __init__(self):
        self.order_service = OrderService()

    @order_router.post("/order", status_code=HTTP_201_CREATED, operation_id="create_order_post")
    def create_order(self, order: OrderSchema) -> OrderSchema:
        order_orm: OrderOrm = order.to_orm()  # convert pydantic to sqlalchemy

        return self.order_service.create_order(order_orm)

    @order_router.get("/order/{order_id}", operation_id="retrieve_order_get")
    def retrieve_order(self, order_id: str) -> OrderSchema:
        return self.order_service.get_order(order_id)

    @order_router.get("/order/address/{address_id}", operation_id="retrieve_order_by_address_get")
    def retrieve_order_by_address(self, address_id: str) -> OrderSchema:
        return self.order_service.get_order_by_address_id(address_id)

    @order_router.put("/order/{order_id}", operation_id="update_order_put")
    def update_order(self, order_id: str, order: OrderSchema) -> OrderSchema:
        order_orm: OrderOrm = order.to_orm()  # convert pydantic to sqlalchemy

        return self.order_service.update_order(order_id, order_orm)

    @order_router.get("/orders", operation_id="list_orders_get")
    def list_orders(self, pageable: PageRequestSchema = Depends()) -> PageResponseSchema:
        data, total_count = self.order_service.get_paged_orders(pageable)
        pydantic_orders = [OrderSchema.from_orm(orm) for orm in data]  # needed to serialize correctly
        return PageResponseSchema(total_count=total_count, page_size=pageable.size, data=pydantic_orders)
