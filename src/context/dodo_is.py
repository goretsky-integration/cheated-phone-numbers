from collections.abc import Iterable

from connections.dodo_is import DodoIsConnection
from models import AccountCookies, Order, Unit
from parsers.dodo_is import (
    filter_by_length,
    filter_have_phone_number,
    group_by_phone_number,
    parse_dodo_is_orders_response,
)
from time_helpers import Period

__all__ = ('DodoIsContext',)


class DodoIsContext:

    def __init__(self, connection: DodoIsConnection):
        self.__connection = connection

    def get_orders(
            self,
            *,
            account_cookies: AccountCookies,
            period: Period,
            units: Iterable[Unit],
            min_orders_count: int,
    ) -> list[list[Order]]:
        unit_ids = [unit.id for unit in units]

        response = self.__connection.get_orders(
            unit_ids=unit_ids,
            cookies=account_cookies.cookies,
            start=period.start,
            end=period.end,
        )
        orders = parse_dodo_is_orders_response(response=response)

        orders_with_phone_number = filter_have_phone_number(orders)
        grouped_orders = group_by_phone_number(orders_with_phone_number)
        return filter_by_length(
            nested_items=grouped_orders,
            min_length=min_orders_count,
        )
