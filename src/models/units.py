from pydantic import BaseModel

__all__ = ('Unit',)


class Unit(BaseModel):
    id: int
    name: str
