import asyncio

from fast_depends import Depends, inject
from faststream.rabbit import RabbitBroker

from config import Config, load_config
from connections.cheated_orders_state_manager import CheatedOrdersStateManager
from context.auth_credentials_storage import AuthCredentialsContext
from context.dodo_is import DodoIsContext
from context.message_queue import publish_events
from dependencies.auth_credentials_storage import (
    get_auth_credentials_context,
)
from dependencies.dodo_is import get_dodo_is_context
from dependencies.message_queue import get_message_queue_broker
from dependencies.cheated_orders_state_manager import (
    get_cheated_orders_state_manager,
)
from models import AccountUnits, Event
from parsers.dodo_is import prepare_events
from time_helpers import Period
from units_storage import load_units


@inject
async def main(
        accounts_units: list[AccountUnits] = Depends(load_units),
        auth_credentials_context: (
                AuthCredentialsContext
        ) = Depends(get_auth_credentials_context),
        dodo_is_context: DodoIsContext = Depends(get_dodo_is_context),
        config: Config = Depends(load_config),
        broker: RabbitBroker = Depends(get_message_queue_broker),
        cheated_orders_state_manager: CheatedOrdersStateManager = Depends(
            get_cheated_orders_state_manager,
        ),
) -> None:
    period = Period.today(timezone=config.timezone)

    events: list[Event] = []
    for account_units in accounts_units:
        unit_name_to_id = {unit.name: unit.id for unit in account_units.units}

        account_cookies = auth_credentials_context.get_account_cookies(
            account_name=account_units.account_name,
        )
        grouped_orders = dodo_is_context.get_orders(
            units=account_units.units,
            account_cookies=account_cookies,
            period=period,
            min_orders_count=config.min_orders_count,
        )

        events += prepare_events(
            grouped_orders=grouped_orders,
            unit_name_to_id=unit_name_to_id,
        )

    new_events = await cheated_orders_state_manager.filter(events)
    print(new_events)
    await publish_events(broker=broker, events=new_events)
    await cheated_orders_state_manager.save(events)


if __name__ == '__main__':
    asyncio.run(main())
