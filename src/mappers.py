from collections import defaultdict
from collections.abc import Iterable
from typing import TypeAlias

from models import (
    AccountUnits,
    Event,
    EventPayload,
    EventPayloadOrder,
    Order,
    Unit,
)

__all__ = (
    'map_orders_to_events',
    'group_by_phone_number_and_unit_name',
    'map_accounts_units_to_units',
)

UnitNameAndPhoneNumber: TypeAlias = tuple[str, str]
UnitNameAndPhoneNumberToOrders: TypeAlias = (
    dict[UnitNameAndPhoneNumber, list[Order]]
)


def group_by_phone_number_and_unit_name(
        orders: Iterable[Order],
) -> UnitNameAndPhoneNumberToOrders:
    unit_name_and_phone_number_to_orders: UnitNameAndPhoneNumberToOrders = (
        defaultdict(list)
    )

    for order in orders:
        phone_number_and_unit_name = (order.unit_name, order.phone_number)
        unit_name_and_phone_number_to_orders[phone_number_and_unit_name].append(
            order,
        )

    return dict(unit_name_and_phone_number_to_orders)


def map_orders_to_events(
        *,
        orders: Iterable[Order],
        units: Iterable[Unit],
        orders_count_threshold: int,
) -> list[Event]:
    unit_name_to_id = {unit.name: unit.id for unit in units}
    unit_name_and_phone_number_to_orders = group_by_phone_number_and_unit_name(
        orders=orders,
    )

    events: list[Event] = []
    for (unit_name, phone_number), orders in (
            unit_name_and_phone_number_to_orders.items()
    ):
        if len(orders) < orders_count_threshold:
            continue
        unit_id = unit_name_to_id[unit_name]

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
        event = Event(unit_ids=unit_id, payload=event_payload)
        events.append(event)

    return events


def map_accounts_units_to_units(
        accounts_units: Iterable[AccountUnits],
) -> list[Unit]:
    return [
        unit
        for account_units in accounts_units
        for unit in account_units.units
    ]
