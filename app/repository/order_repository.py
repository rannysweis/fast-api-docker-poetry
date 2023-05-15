import logging

from sqlalchemy import or_, select
from sqlalchemy.exc import NoResultFound

from app.models.order import OrderOrm
from app.repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class OrderRepository(BaseRepository):
    def __init__(self):
        super().__init__(OrderOrm)

    async def get_by_address_id(self, address_id):
        async with self.session_maker as session:
            try:
                clause = or_(OrderOrm.pickup_id == address_id, OrderOrm.dropoff_id == address_id)
                result = await session.execute(select(self.__model__).filter(clause))
                return result.one()[0]
            except NoResultFound as e:
                logger.exception(f'{self.__model__.__name__} not found with address id: {id}')
                raise e
