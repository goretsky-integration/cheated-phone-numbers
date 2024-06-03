import pathlib

from pydantic import TypeAdapter

import config
from models import AccountUnits

__all__ = ('load_units',)


def load_units(
        file_path: pathlib.Path = config.UNITS_FILE_PATH,
) -> list[AccountUnits]:
    type_adapter = TypeAdapter(list[AccountUnits])
    config_json = file_path.read_text(encoding='utf-8')
    return type_adapter.validate_json(config_json)
