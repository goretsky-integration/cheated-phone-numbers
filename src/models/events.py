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
    unit_ids: int
    type: str = Field(default='CHEATED_PHONE_NUMBERS', frozen=True)
    payload: EventPayload
