import asyncio
from dataclasses import dataclass

from connections.auth_credentials_storage import (
    AuthCredentialsStorageConnection,
)
from models import AccountCookies
from parsers.auth_credentials import parse_account_cookies_response

__all__ = (
    'AccountCookiesFetchAllResult',
    'AccountCookiesFetcher',
    'AccountCookiesFetchResult',
)


@dataclass(frozen=True, slots=True)
class AccountCookiesFetchResult:
    account_name: str
    account_cookies: AccountCookies | None = None
    exception: Exception | None = None


@dataclass(frozen=True, slots=True)
class AccountCookiesFetchAllResult:
    accounts_cookies: list[AccountCookies]
    error_account_names: set[str]


class AccountCookiesFetcher:

    def __init__(self, connection: AuthCredentialsStorageConnection):
        self.__connection = connection
        self.__account_names_registry: set[str] = set()

    def register_account_name(self, account_name: str) -> None:
        self.__account_names_registry.add(account_name)

    async def __get_account_cookies(
            self,
            account_name: str,
    ) -> AccountCookiesFetchResult:
        try:
            response = await self.__connection.get_cookies(account_name)
            account_cookies = parse_account_cookies_response(response)
        except Exception as error:
            return AccountCookiesFetchResult(
                account_name=account_name,
                exception=error,
            )
        return AccountCookiesFetchResult(
            account_name=account_name,
            account_cookies=account_cookies,
        )

    async def fetch_all(self) -> AccountCookiesFetchAllResult:
        tasks: list[asyncio.Task[AccountCookiesFetchResult]] = []

        async with asyncio.TaskGroup() as task_group:
            for account_name in self.__account_names_registry:
                task = task_group.create_task(
                    self.__get_account_cookies(account_name),
                )
                tasks.append(task)

        accounts_cookies: list[AccountCookies] = []
        error_account_names: set[str] = set()
        for task in tasks:
            account_cookies_fetch_result = task.result()

            if account_cookies_fetch_result.account_cookies is not None:
                accounts_cookies.append(
                    account_cookies_fetch_result.account_cookies,
                )

            if account_cookies_fetch_result.exception is not None:
                error_account_names.add(
                    account_cookies_fetch_result.account_name,
                )

        return AccountCookiesFetchAllResult(
            accounts_cookies=accounts_cookies,
            error_account_names=error_account_names,
        )
