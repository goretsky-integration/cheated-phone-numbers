from datetime import datetime

import httpx
from bs4 import BeautifulSoup, Tag

from models import Order

__all__ = ('parse_dodo_is_orders_response',)


def parse_dodo_is_orders_response(
        response: httpx.Response,
) -> list[Order]:
    soup = BeautifulSoup(response.text, 'lxml')
    table_body: Tag | None = soup.find('tbody')

    if table_body is None:
        raise

    table_rows = table_body.find_all('tr')

    orders: list[Order] = []

    for table_row in table_rows:
        table_row_data: list[Tag] = table_row.find_all('td')

        unit_name = table_row_data[1].text
        created_at = table_row_data[2].text
        order_number = table_row_data[3].text
        phone_number = table_row_data[6].text

        phone_number = phone_number or None

        created_at = datetime.strptime(created_at, '%d.%m.%Y %H:%M')

        order = Order(
            unit_name=unit_name,
            created_at=created_at,
            number=order_number,
            phone_number=phone_number,
        )
        orders.append(order)

    return orders
