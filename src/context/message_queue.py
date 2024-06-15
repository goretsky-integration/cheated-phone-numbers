from collections.abc import Iterable

from faststream.rabbit import RabbitBroker

from models import Event

__all__ = ('publish_events',)


async def publish_events(events: Iterable[Event], broker: RabbitBroker) -> None:
    for event in events:
        await broker.publish(
            message=event.model_dump(),
            queue='specific-units-event',
        )
