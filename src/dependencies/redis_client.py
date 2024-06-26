import redis.asyncio as redis
from fast_depends import Depends

from config import Config, load_config

__all__ = ('get_redis_client',)


async def get_redis_client(
        config: Config = Depends(load_config),
) -> redis.Redis:
    async with redis.from_url(
            url=config.redis_url,
            decode_responses=True,
    ) as connection:
        yield connection
