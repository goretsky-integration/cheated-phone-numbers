from datetime import datetime

from pydantic import BaseModel

__all__ = ('Order',)


class Order(BaseModel):
    unit_name: str
    created_at: datetime
    number: str
    phone_number: str | None
