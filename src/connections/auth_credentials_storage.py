import httpx
import structlog.stdlib
from structlog.contextvars import bound_contextvars

from new_types import AuthCredentialsStorageHttpClient

__all__ = ('AuthCredentialsStorageConnection',)

logger = structlog.stdlib.get_logger('connection')


class AuthCredentialsStorageConnection:

    def __init__(self, http_client: AuthCredentialsStorageHttpClient):
        self.__http_client = http_client

    def get_cookies(self, account_name: str) -> httpx.Response:
        url = '/auth/cookies/'
        query_params = {'account_name': account_name}
        with bound_contextvars(account_name=account_name):
            logger.debug(
                'Sending request to auth credentials storage'
            )
            response = self.__http_client.get(url, params=query_params)
            logger.debug(
                'Received response from auth credentials storage',
                status_code=response.status_code
            )
        return response
