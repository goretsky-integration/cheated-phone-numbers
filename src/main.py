import asyncio

from fast_depends import Depends, inject
from faststream.rabbit import RabbitBroker

from config import Config, load_config
from connections.auth_credentials_storage import \
    AuthCredentialsStorageConnection
from connections.cheated_orders_state_manager import CheatedOrdersStateManager
from connections.dodo_is import DodoIsConnection
from context.auth_credentials_storage import AccountCookiesFetcher
from context.dodo_is import OrdersFetcher
from context.message_queue import publish_events
from dependencies.auth_credentials_storage import \
    get_auth_credentials_storage_connection
from dependencies.cheated_orders_state_manager import (
    get_cheated_orders_state_manager,
)
from dependencies.dodo_is import get_dodo_is_connection
from dependencies.message_queue import get_message_queue_broker
from filters import filter_orders_with_phone_numbers
from mappers import map_accounts_units_to_units, map_orders_to_events
from models import AccountUnits
from time_helpers import Period
from units_storage import load_units


@inject
async def main(
        accounts_units: list[AccountUnits] = Depends(load_units),
        auth_credentials_storage_connection: (
                AuthCredentialsStorageConnection
        ) = Depends(get_auth_credentials_storage_connection),
        dodo_is_connection: DodoIsConnection = Depends(get_dodo_is_connection),
        config: Config = Depends(load_config),
        broker: RabbitBroker = Depends(get_message_queue_broker),
        cheated_orders_state_manager: CheatedOrdersStateManager = Depends(
            get_cheated_orders_state_manager,
        ),
) -> None:
    period = Period.today(timezone=config.timezone)

    account_cookies_fetcher = AccountCookiesFetcher(
        connection=auth_credentials_storage_connection,
    )
    for account_units in accounts_units:
        account_cookies_fetcher.register_account_name(
            account_name=account_units.account_name,
        )

    account_name_to_units = {
        account_units.account_name: account_units.units
        for account_units in accounts_units
    }
    account_cookies_fetch_result = await account_cookies_fetcher.fetch_all()

    for account_name in account_cookies_fetch_result.error_account_names:
        print(f'Failed to fetch cookies for account "{account_name}"')

    orders_fetcher = OrdersFetcher(dodo_is_connection)

    for account_cookies in account_cookies_fetch_result.accounts_cookies:
        units = account_name_to_units[account_cookies.account_name]
        orders_fetcher.register_task(
            account_cookies=account_cookies,
            units=units,
        )

    orders_fetch_result = await orders_fetcher.fetch_all(period=period)

    orders = filter_orders_with_phone_numbers(orders_fetch_result.orders)

    events = map_orders_to_events(
        orders=orders,
        units=map_accounts_units_to_units(accounts_units),
        orders_count_threshold=3,
    )

    new_events = await cheated_orders_state_manager.filter(events)

    await publish_events(broker=broker, events=new_events)
    await cheated_orders_state_manager.save(events)


if __name__ == '__main__':
    asyncio.run(main())
