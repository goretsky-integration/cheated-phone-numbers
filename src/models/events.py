from datetime import datetime

from pydantic import BaseModel, Field

__all__ = ('Event', 'EventPayload', 'EventPayloadOrder')


class EventPayloadOrder(BaseModel):
    number: str
    created_at: datetime


class EventPayload(BaseModel):
    unit_name: str
    phone_number: str
    orders: list[EventPayloadOrder]


class Event(BaseModel):
    unit_ids: list[int]
    type: str = Field(default='CANCELED_ORDERS', frozen=True)
    payload: EventPayload