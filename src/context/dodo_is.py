import asyncio
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeAlias

from connections.dodo_is import DodoIsConnection
from models import AccountCookies, Order, Unit
from parsers.dodo_is import parse_dodo_is_orders_response
from time_helpers import Period

__all__ = (
    'OrdersFetcher',
    'OrdersFetchAllResult',
    'OrdersFetchResult',
)

AccountCookiesAndUnits: TypeAlias = tuple[AccountCookies, tuple[Unit, ...]]


@dataclass(frozen=True, slots=True)
class OrdersFetchResult:
    units: list[Unit]
    orders: list[Order] | None = None
    exception: Exception | None = None


@dataclass(frozen=True, slots=True)
class OrdersFetchAllResult:
    orders: list[Order]
    error_units: list[Unit]


class OrdersFetcher:

    def __init__(self, connection: DodoIsConnection):
        self.__connection = connection
        self.__tasks_registry: list[AccountCookiesAndUnits] = []

    def register_task(
            self,
            *,
            account_cookies: AccountCookies,
            units: Iterable[Unit],
    ) -> None:
        self.__tasks_registry.append((account_cookies, tuple(units)))

    async def __get_orders(
            self,
            *,
            period: Period,
            account_cookies: AccountCookies,
            units: Iterable[Unit],
    ) -> OrdersFetchResult:
        try:
            response = await self.__connection.get_orders(
                unit_ids=[unit.id for unit in units],
                cookies=account_cookies.cookies,
                start=period.start,
                end=period.end,
            )
            orders = parse_dodo_is_orders_response(response)
        except Exception as error:
            return OrdersFetchResult(units=list(units), exception=error)
        return OrdersFetchResult(units=list(units), orders=orders)

    async def fetch_all(
            self,
            period: Period,
    ) -> OrdersFetchAllResult:
        tasks: list[asyncio.Task[OrdersFetchResult]] = []
        async with asyncio.TaskGroup() as task_group:
            for account_cookies, units in self.__tasks_registry:
                task = task_group.create_task(
                    self.__get_orders(
                        period=period,
                        account_cookies=account_cookies,
                        units=units,
                    )
                )
                tasks.append(task)

        orders: list[Order] = []
        error_units: list[Unit] = []
        for task in tasks:
            orders_fetch_result = task.result()

            if orders_fetch_result.orders is not None:
                orders += orders_fetch_result.orders

            if orders_fetch_result.exception is not None:
                error_units += orders_fetch_result.units

        return OrdersFetchAllResult(orders=orders, error_units=error_units)
