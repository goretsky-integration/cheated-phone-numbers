from fast_depends import Depends
from faststream.rabbit import RabbitBroker

from config import Config, load_config

__all__ = ('get_message_queue_broker',)


async def get_message_queue_broker(
        config: Config = Depends(load_config),
) -> RabbitBroker:
    async with RabbitBroker(url=config.message_queue_url) as broker:
        yield broker
