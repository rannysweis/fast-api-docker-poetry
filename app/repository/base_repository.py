import logging

from sqlalchemy.exc import IntegrityError, ProgrammingError, NoResultFound

from app.models.base import BaseOrm
from app.utils.db import get_db

logger = logging.getLogger(__name__)


class BaseRepository(object):
    __abstract__ = True

    def __init__(self, model: BaseOrm):
        self.__model__ = model

    def save(self, data):
        with get_db() as db:
            try:
                db.add(data)
                db.commit()
                db.flush()
                db.refresh(data)
                return data
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e

    def insert(self, obj, **kwargs):
        db_obj = self.__model__(**obj.__dict__)
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        return self.save(db_obj)

    def update(self, request, obj):
        for key, value in request.__dict__.items():
            if key in request.editable_fields:
                setattr(obj, key, value)
        return self.save(obj)

    def delete(self, data):
        with get_db() as db:
            try:
                db.delete(data)
                db.commit()
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e

    def get_by_id(self, id, *args):
        with get_db() as db:
            try:
                return db.query(self.__model__).filter_by(id=id).one()
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

    def delete_by_id(self, id):
        with get_db() as db:
            db.query(self.__model__).filter_by(id=id).delete()
            db.commit()

    def get_by_ids(self, ids, *args):
        with get_db() as db:
            try:
                return db.query(self.__model__).filter(self.__model__.id.in_(ids)).all()
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

    def get_paged_items(self, pageable, params):
        with get_db() as db:
            try:
                data = []
                total_count = db.query(self.__model__).filter_by(**params).count()
                if total_count > 0:
                    query = db.query(self.__model__).filter_by(**params)
                    data = pageable.build(query, getattr(self.__model__, pageable.sort)).all()
                return data, total_count
            except IntegrityError as e:
                logger.exception(f'{self.__model__.__name__} error: {e.orig}')
                raise e
            except ProgrammingError as e:
                logger.exception(f'{self.__model__.__name__} error: {e}')
                raise e
