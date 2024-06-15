import httpx

from models import AccountCookies

__all__ = ('parse_account_cookies_response',)


def parse_account_cookies_response(response: httpx.Response) -> AccountCookies:
    response_data = response.json()
    return AccountCookies.model_validate(response_data)
