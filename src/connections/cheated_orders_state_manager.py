from collections.abc import Iterable
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import redis.asyncio as redis

from models import Event

__all__ = (
    'compute_state_reset_time',
    'StopSalesStateManager',
    'build_key',
)


def build_key(phone_number: str, unit_name: str) -> str:
    return f'cheated-orders@{phone_number}@{unit_name}'


def compute_state_reset_time(timezone: ZoneInfo):
    tomorrow_this_moment = datetime.now(timezone) + timedelta(days=1)
    return tomorrow_this_moment.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


class CheatedOrdersStateManager:
    key = 'cheated-orders'

    def __init__(self, redis_client: redis.Redis, timezone: ZoneInfo):
        self.__redis_client = redis_client
        self.__timezone = timezone

    async def filter(self, events: Iterable[Event]):
        """Filter out stop sales that are already in the state."""
        result: list[Event] = []

        for event in events:
            key = build_key(
                unit_name=event.payload.unit_name,
                phone_number=event.payload.phone_number
            )
            count = await self.__redis_client.get(key) or 0

            if len(event.payload.orders) <= count:
                continue

            result.append(event)

        return result

    async def save(self, events: Iterable[Event]) -> None:
        """Save stop sales to the state."""
        reset_time = compute_state_reset_time(self.__timezone)

        for event in events:
            key = build_key(
                unit_name=event.payload.unit_name,
                phone_number=event.payload.phone_number
            )
            value = len(event.payload.orders)
            await self.__redis_client.set(key, value, exat=reset_time)
