import logging

from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError, ProgrammingError, NoResultFound

from app.models.base import BaseOrm
from app.utils.async_db import get_async_db

logger = logging.getLogger(__name__)


class BaseRepository(object):
    __abstract__ = True

    def __init__(self, model: BaseOrm):
        self.__model__ = model

    async def save(self, data):
        async with get_async_db() as db:
            try:
                db.add(data)
                await db.commit()
                await db.flush()
                await db.refresh(data)
                return data
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e

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
        async with get_async_db() as db:
            try:
                await db.delete(data)
                await db.commit()
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e

    async def get_by_id(self, id, *args):
        async with get_async_db() as db:
            try:
                # return db.query(self.__model__).filter_by(id=id).one()
                execute = await db.execute(select(self.__model__).filter_by(id=id))
                return execute.one()[0]
            except NoResultFound as e:
                if args:
                    return args[0]
                logger.exception(f'{self.__model__.__name__} not found with id: {id}')
                raise e
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e

    async def delete_by_id(self, id):
        async with get_async_db() as db:
            # db.query(self.__model__).filter_by(id=id).delete()
            await db.execute(delete(self.__model__).filter_by(id=id))
            await db.commit()

    async def get_by_ids(self, ids, *args):
        async with get_async_db() as db:
            try:
                # return db.query(self.__model__).filter(self.__model__.id.in_(ids)).all()
                return await db.execute(select(self.__model__).filter(self.__model__.id.in_(ids))).fetchall()
            except NoResultFound as e:
                if args:
                    return args[0]
                logger.exception(f'{self.__model__.__name__} not found with id: {id}')
                raise e
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e

    async def get_paged_items(self, pageable, params):
        async with get_async_db() as db:
            try:
                data = []
                # total_count = db.query(self.__model__).filter_by(**params).count()
                execute = await db.execute(select(func.count()).select_from(self.__model__).filter_by(**params))
                total_count = execute.scalar()
                if total_count > 0:
                    # query = db.query(self.__model__).filter_by(**params)
                    sort = getattr(self.__model__, pageable.sort)
                    execute = await db.execute(
                        select(self.__model__).filter_by(**params).order_by(pageable.sql_sort(sort))
                        .limit(pageable.size).offset(pageable.offset)
                    )
                    data = execute.scalars().all()
                return data, total_count
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e
