from sqlalchemy import select, delete, func
from sqlalchemy.exc import NoResultFound

from app.models.base import BaseOrm
from app.models.pageable import PageRequestSchema
from app.utils.db_session import sessionmaker, get_db_session


class BaseRepository:
    __abstract__ = True

    def __init__(self, model: BaseOrm):
        self.__model__ = model

    async def save(self, data):
        async with get_db_session() as session:
            session.add(data)
            return data

    async def delete(self, data):
        async with get_db_session() as session:
            await session.delete(data)

    async def get_by_id(self, id, *args):
        async with get_db_session() as session:
            try:
                execute = await session.execute(select(self.__model__).filter_by(id=id))
                return execute.one()[0]
            except NoResultFound as e:
                if args:
                    return args[0]
                raise e

    async def delete_by_id(self, entity_id: int):
        async with get_db_session() as session:
            await session.execute(delete(self.__model__).filter_by(id=entity_id))

    async def get_by_ids(self, ids, *args):
        async with get_db_session() as session:
            try:
                return await session.execute(select(self.__model__).filter(self.__model__.id.in_(ids))).fetchall()
            except NoResultFound as e:
                if args:
                    return args[0]
                raise e

    async def get_paged_items(self, pageable: PageRequestSchema, params: dict):
        async with get_db_session() as session:
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
