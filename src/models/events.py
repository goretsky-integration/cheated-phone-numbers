from datetime import datetime
from uuid import UUID

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
    unit_ids: UUID
    type: str = Field(default='CHEATED_PHONE_NUMBERS', frozen=True)
    payload: EventPayload
