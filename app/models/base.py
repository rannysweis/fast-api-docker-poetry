from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from pydantic import BaseModel
from pydantic import Field
from sqlalchemy import Column, DateTime, BigInteger
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

"""
alembic requires constraints to be named.
This sets up a naming convention rather than manually naming
https://alembic.sqlalchemy.org/en/latest/naming.html
"""
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
meta = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
Base = declarative_base(metadata=meta)  # ORM base class


class BaseOrm(Base):
    """
    Provides primary key column, created and updated timestamps
    """

    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=datetime.utcnow(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )


class BaseSchema(BaseModel):
    __orm__ = None
    __transient_fields__ = ["id", "created_at", "updated_at"]

    class Config:
        orm_mode = True

    id: Optional[int] = Field(default=None, read_only=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    def to_orm(self):
        if not self.__orm__:
            raise NotImplementedError("Error __orm__ class not set")

        orm = self.__orm__()

        def set_val(key, data):
            if (isinstance(data, BaseOrm) or isinstance(data, list)) and key not in self.__transient_fields__:
                setattr(orm, key, data)
            else:
                for key, value in data:
                    try:
                        if isinstance(value, list):
                            set_val(key, [item.to_orm() for item in value if isinstance(item, BaseSchema)])
                        elif isinstance(value, BaseSchema) and key not in self.__transient_fields__:
                            setattr(orm, key, value.to_orm())
                        elif value is not None and key not in self.__transient_fields__:
                            setattr(orm, key, value)
                    except AttributeError as e:
                        pass

        set_val(None, self)

        return orm
