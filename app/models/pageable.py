import math
from typing import List, Optional, Literal, Any

from pydantic import BaseModel
from sqlalchemy.orm import Query


class PageRequestSchema(BaseModel):
    page: Optional[int] = 1
    size: Optional[int] = 25
    sort: Optional[str] = 'created_at'
    direction: Optional[Literal['ASC', 'DESC']] = 'DESC'

    @property
    def offset(self):
        return (self.page - 1) * self.size

    def build(self, query: Query, sort):
        sort = sort.asc() if self.direction == "ASC" else sort.desc()
        return query.order_by(sort).limit(self.size).offset(self.offset)


class PageResponseSchema(BaseModel):
    data: List[Any]
    total_pages: Optional[int]
    total_count: int
    page_size: int

    def __init__(self, **data):
        super().__init__(**data)

        self.total_pages = math.ceil(self.total_count / self.page_size)


