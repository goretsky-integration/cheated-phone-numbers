import httpx
from fast_depends import Depends

from config import Config, load_config
from connections.auth_credentials_storage import (
    AuthCredentialsStorageConnection,
)
from new_types import AuthCredentialsStorageHttpClient

__all__ = (
    'get_auth_credentials_storage_http_client',
    'get_auth_credentials_storage_connection',
)


async def get_auth_credentials_storage_http_client(
        config: Config = Depends(load_config),
) -> AuthCredentialsStorageHttpClient:
    async with httpx.AsyncClient(
            base_url=config.auth_credentials_storage.base_url,
            timeout=config.auth_credentials_storage.timeout,
    ) as http_client:
        yield AuthCredentialsStorageHttpClient(http_client)


def get_auth_credentials_storage_connection(
        http_client: AuthCredentialsStorageHttpClient = Depends(
            get_auth_credentials_storage_http_client,
        ),
) -> AuthCredentialsStorageConnection:
    return AuthCredentialsStorageConnection(http_client)
