import pathlib
import tomllib
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from enums import CountryCode

__all__ = (
    'UNITS_FILE_PATH',
    'CONFIG_FILE_PATH',
    'STATE_STORAGE_FILE_PATH',
    'load_config',
    'Config',
)

UNITS_FILE_PATH = pathlib.Path(__file__).parent.parent / 'accounts_units.json'
CONFIG_FILE_PATH = pathlib.Path(__file__).parent.parent / 'config.toml'
STATE_STORAGE_FILE_PATH = (
        pathlib.Path(__file__).parent.parent / 'state_storage.db'
)


@dataclass(frozen=True, slots=True)
class AuthCredentialsStorageConfig:
    timeout: int | float
    base_url: str


@dataclass(frozen=True, slots=True)
class Config:
    timezone: ZoneInfo
    app_name: str
    country_code: str
    message_queue_url: str
    min_orders_count: int
    dodo_is_http_client_timeout: int | float
    auth_credentials_storage: AuthCredentialsStorageConfig


def load_config(file_path: pathlib.Path = CONFIG_FILE_PATH) -> Config:
    config_toml = file_path.read_text(encoding='utf-8')
    config = tomllib.loads(config_toml)

    message_queue_url = config['message_queue']['url']
    app_name = config['app']['name']
    timezone = ZoneInfo(config['app']['timezone'])
    country_code = CountryCode(config['app']['country_code'].lower())
    min_orders_count = config['app']['min_orders_count']
    dodo_is_timeout = config['dodo_is']['timeout']
    auth_credentials_storage = AuthCredentialsStorageConfig(
        timeout=config['auth_credentials_storage']['timeout'],
        base_url=config['auth_credentials_storage']['base_url'],
    )

    return Config(
        app_name=app_name,
        timezone=timezone,
        country_code=country_code,
        message_queue_url=message_queue_url,
        min_orders_count=min_orders_count,
        dodo_is_http_client_timeout=dodo_is_timeout,
        auth_credentials_storage=auth_credentials_storage,
    )
