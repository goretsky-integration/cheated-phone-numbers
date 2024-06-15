from collections.abc import Iterable, Sized
from typing import TypeVar

from models import Order

__all__ = (
    'filter_orders_with_phone_numbers',
)

T = TypeVar('T', bound=Sized)


def filter_orders_with_phone_numbers(orders: Iterable[Order]) -> list[Order]:
    return [order for order in orders if order.phone_number is not None]
