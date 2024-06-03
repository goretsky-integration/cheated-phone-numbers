from collections import defaultdict
from collections.abc import Iterable, Mapping, Sized
from datetime import datetime
from typing import TypeAlias, TypeVar

import httpx
from bs4 import BeautifulSoup, Tag

from models import Event, EventPayload, EventPayloadOrder, Order

__all__ = (
    'parse_dodo_is_orders_response',
    'filter_have_phone_number',
    'group_by_phone_number',
    'filter_by_length',
    'prepare_events',
)

PhoneNumberAndUnitName: TypeAlias = tuple[str, str]
PhoneNumberAndUnitNameToOrders: Mapping[PhoneNumberAndUnitName, list[Order]]

T = TypeVar('T', bound=Sized)


def filter_by_length(
        nested_items: Iterable[T],
        min_length: int,
) -> list[T]:
    return [
        items for items in nested_items
        if len(items) > min_length
    ]


def group_by_phone_number(orders: Iterable[Order]) -> tuple[list[Order], ...]:
    phone_number_to_orders: PhoneNumberAndUnitNameToOrders = defaultdict(list)

    for order in orders:
        phone_number_and_unit_name = (order.phone_number, order.unit_name)
        phone_number_to_orders[phone_number_and_unit_name].append(order)

    return tuple(phone_number_to_orders.values())


def filter_have_phone_number(orders: Iterable[Order]) -> list[Order]:
    return [order for order in orders if order.phone_number is not None]


def parse_dodo_is_orders_response(
        response: httpx.Response,
) -> list[Order]:
    soup = BeautifulSoup(response.text, 'lxml')
    table_body: Tag | None = soup.find('tbody')

    if table_body is None:
        raise

    table_rows = table_body.find_all('tr')

    orders: list[Order] = []

    for table_row in table_rows:
        table_row_data: list[Tag] = table_row.find_all('td')

        unit_name = table_row_data[1].text
        created_at = table_row_data[2].text
        order_number = table_row_data[3].text
        phone_number = table_row_data[6].text

        phone_number = phone_number or None

        created_at = datetime.strptime(created_at, '%d.%m.%Y %H:%M')

        order = Order(
            unit_name=unit_name,
            created_at=created_at,
            number=order_number,
            phone_number=phone_number,
        )
        orders.append(order)

    return orders


def prepare_events(
        grouped_orders: Iterable[list[Order]],
        unit_name_to_id: Mapping[str, int],
) -> list[Event]:
    events: list[Event] = []
    for orders in grouped_orders:
        order = orders[0]

        unit_id = unit_name_to_id[order.unit_name]
        unit_name = order.unit_name
        phone_number = order.phone_number

        event_payload_orders = [
            EventPayloadOrder(
                number=order.number,
                created_at=order.created_at,
            )
            for order in orders
        ]
        event_payload = EventPayload(
            unit_name=unit_name,
            phone_number=phone_number,
            orders=event_payload_orders,
        )
        event = Event(unit_ids=[unit_id], payload=event_payload)
        events.append(event)

    return events
