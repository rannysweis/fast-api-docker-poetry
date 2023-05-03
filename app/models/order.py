import random
import string
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Float,
    ForeignKey, BigInteger,
)
from sqlalchemy.orm import relationship

from app.models.address import AddressOrm, AddressSchema
from app.models.base import BaseOrm, BaseSchema


class OrderOrm(BaseOrm):
    __tablename__ = "orders"

    order_number = Column(String, default=lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
    name = Column(String)
    price = Column(Float)
    pickup_id = Column(BigInteger, ForeignKey("addresses.id"))
    dropoff_id = Column(BigInteger, ForeignKey("addresses.id"))

    pickup_address = relationship(AddressOrm, foreign_keys="OrderOrm.pickup_id", lazy="joined", cascade="all,delete")
    dropoff_address = relationship(AddressOrm, foreign_keys="OrderOrm.dropoff_id", lazy="joined", cascade="all,delete")


class OrderSchema(BaseSchema):
    __orm__ = OrderOrm

    order_number: Optional[str]
    name: Optional[str]
    price: float
    pickup_address: Optional[AddressSchema]
    dropoff_address: Optional[AddressSchema]

