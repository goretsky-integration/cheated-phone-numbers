from collections.abc import Iterable, Mapping
from datetime import datetime

from new_types import DodoIsHttpClient

__all__ = ('DodoIsConnection',)


class DodoIsConnection:

    def __init__(self, http_client: DodoIsHttpClient):
        self.__http_client = http_client

    async def get_orders(
            self,
            *,
            unit_ids: Iterable[int],
            start: datetime,
            end: datetime,
            cookies: Mapping[str, str],
    ):
        url = '/Reports/Orders/Get'
        request_data = {
            'filterType': 'OrdersFromRestaurant',
            'unitsIds': tuple(unit_ids),
            'OrderSources': ['Restaurant', 'Pizzeria'],
            'beginDate': start.strftime('%d.%m.%Y'),
            'endDate': end.strftime('%d.%m.%Y'),
            'orderTypes': ['Stationary']
        }
        response = await self.__http_client.post(
            url=url,
            data=request_data,
            cookies=dict(cookies),
        )
        return response
