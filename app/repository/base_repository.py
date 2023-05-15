import logging

from sqlalchemy import select, delete, func
from sqlalchemy.exc import NoResultFound

from app.config.settings import get_database_settings
from app.models.base import BaseOrm
from app.models.pageable import PageRequestSchema
from app.utils.async_session_maker import AsyncSessionMaker

logger = logging.getLogger(__name__)
async_url = get_database_settings().async_url


class BaseRepository:
    __abstract__ = True

    def __init__(self, model: BaseOrm):
        self.__model__ = model
        self.session_maker = AsyncSessionMaker(async_url).cached_sessionmaker()

    async def save(self, data):
        async with self.session_maker as session:
            session.add(data)
            await session.commit()
            return data

    async def insert(self, obj, **kwargs):
        db_obj = self.__model__(**obj.__dict__)
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        return await self.save(db_obj)

    # async def update(self, request, obj):
    #     for key, value in request.__dict__.items():
    #         if key in request.editable_fields:
    #             setattr(obj, key, value)
    #     return await self.save(obj)

    async def delete(self, data):
        async with self.session_maker as session:
            await session.delete(data)
            await session.commit()

    async def get_by_id(self, id, *args):
        async with self.session_maker as session:
            try:
                execute = await session.execute(select(self.__model__).filter_by(id=id))
                return execute.one()[0]
            except NoResultFound as e:
                if args:
                    return args[0]
                logger.exception(f'{self.__model__.__name__} not found with id: {id}')
                raise e

    async def delete_by_id(self, entity_id: int):
        async with self.session_maker as session:
            await session.execute(delete(self.__model__).filter_by(id=entity_id))
            await session.commit()

    async def get_by_ids(self, ids, *args):
        async with self.session_maker as session:
            try:
                return await session.execute(select(self.__model__).filter(self.__model__.id.in_(ids))).fetchall()
            except NoResultFound as e:
                if args:
                    return args[0]
                logger.exception(f'{self.__model__.__name__} not found with id: {id}')
                raise e

    async def get_paged_items(self, pageable: PageRequestSchema, params: dict):
        async with self.session_maker as session:
            data = []
            execute = await session.execute(select(func.count()).select_from(self.__model__).filter_by(**params))
            total_count = execute.scalar()
            if total_count > 0:
                # query = db.query(self.__model__).filter_by(**params)
                sort = getattr(self.__model__, pageable.sort)
                execute = await session.execute(
                    select(self.__model__).filter_by(**params).order_by(pageable.sql_sort(sort))
                    .limit(pageable.size).offset(pageable.offset)
                )
                data = execute.scalars().all()
            return data, total_count
