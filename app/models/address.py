from typing import Optional

from pydantic import constr
from sqlalchemy import (
    Column,
    String,
    Float,
)

from app.models.base import BaseOrm, BaseSchema


class AddressOrm(BaseOrm):
    __tablename__ = "addresses"

    address_1 = Column(String)
    address_2 = Column(String)
    city = Column(String)
    state_province = Column(String)
    country = Column(String)
    postal_code = Column(String)
    timezone = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class AddressSchema(BaseSchema):
    __orm__ = AddressOrm

    address_1: Optional[str]
    address_2: Optional[str]
    city: Optional[str]
    state_province: Optional[str]
    country: Optional[str]
    postal_code: constr(min_length=5, max_length=10)
    timezone: Optional[str]
    latitude: float
    longitude: float
