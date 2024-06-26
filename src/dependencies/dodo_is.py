import httpx
from fast_depends import Depends

from config import Config, load_config
from connections.dodo_is import DodoIsConnection
from new_types import DodoIsHttpClient

__all__ = (
    'get_dodo_is_http_client',
    'get_dodo_is_connection',
)


async def get_dodo_is_http_client(
        config: Config = Depends(load_config),
) -> DodoIsHttpClient:
    base_url = f'https://officemanager.dodopizza.{config.country_code}'
    async with httpx.AsyncClient(
            timeout=config.dodo_is_http_client_timeout,
            base_url=base_url,
    ) as http_client:
        yield DodoIsHttpClient(http_client)


def get_dodo_is_connection(
        http_client: DodoIsHttpClient = Depends(get_dodo_is_http_client),
) -> DodoIsConnection:
    return DodoIsConnection(http_client)
