import redis.asyncio as redis
from fast_depends import Depends

from config import Config, load_config
from connections.cheated_orders_state_manager import CheatedOrdersStateManager
from dependencies.redis_client import get_redis_client

__all__ = ('get_cheated_orders_state_manager',)


def get_cheated_orders_state_manager(
        config: Config = Depends(load_config),
        redis_client: redis.Redis = Depends(get_redis_client),
) -> CheatedOrdersStateManager:
    return CheatedOrdersStateManager(
        redis_client=redis_client,
        timezone=config.timezone,
    )
