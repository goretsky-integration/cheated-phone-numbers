from uuid import UUID
from pydantic import BaseModel

__all__ = ('Unit',)


class Unit(BaseModel):
    id: UUID
    name: str
