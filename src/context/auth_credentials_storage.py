from connections.auth_credentials_storage import (
    AuthCredentialsStorageConnection,
)
from models import AccountCookies
from parsers.auth_credentials import parse_account_cookies_response

__all__ = ('AuthCredentialsContext',)


class AuthCredentialsContext:

    def __init__(self, connection: AuthCredentialsStorageConnection):
        self.__connection = connection

    def get_account_cookies(self, account_name: str) -> AccountCookies:
        account_cookies_response = self.__connection.get_cookies(account_name)
        return parse_account_cookies_response(account_cookies_response)
