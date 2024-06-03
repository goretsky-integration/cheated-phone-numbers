import sqlite3
from collections.abc import Iterable

from models import Event

__all__ = ('StateStorage', 'filter_new_events')


class StateStorage:

    def __init__(self, connection: sqlite3.Connection):
        self.__connection = connection
        self.__init_tables()

    def __init_tables(self) -> None:
        cursor = self.__connection.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS state ('
            'phone_number TEXT,'
            'unit_name TEXT,'
            'count INTEGER,'
            'PRIMARY KEY (phone_number, unit_name)'
            ');'
        )
        self.__connection.commit()

    def set(self, *, phone_number: str, unit_name: str, count: int) -> None:
        statement = (
            'INSERT INTO state (phone_number, unit_name, count)'
            ' VALUES (?, ?, ?)'
            ' ON CONFLICT (phone_number, unit_name) DO UPDATE SET count = ?;'
        )
        cursor = self.__connection.cursor()
        parameters = (
            phone_number,
            unit_name,
            count,
            phone_number,
            unit_name,
            count,
        )
        cursor.execute(statement, parameters)
        self.__connection.commit()

    def get(self, *, phone_number: str, unit_name: str) -> int:
        statement = (
            'SELECT count FROM state'
            ' WHERE phone_number = ? AND unit_name = ?;'
        )
        cursor = self.__connection.cursor()
        parameters = (phone_number, unit_name)
        cursor.execute(statement, parameters)
        result = cursor.fetchone()
        return result[0] if result is not None else 0

    def reset_all(self) -> None:
        self.__connection.execute('TRUNCATE TABLE state;')
        self.__connection.commit()


def filter_new_events(
        storage: StateStorage,
        events: Iterable[Event],
) -> list[Event]:
    new_events: list[Event] = []

    for event in events:
        count_in_state = storage.get(
            phone_number=event.payload.phone_number,
            unit_name=event.payload.unit_name,
        )

        if len(event.payload.orders) <= count_in_state:
            continue

        new_events.append(event)

    return new_events


def save_events(storage: StateStorage, events: Iterable[Event]) -> None:
    for event in events:
        storage.set(
            phone_number=event.payload.phone_number,
            unit_name=event.payload.unit_name,
            count=len(event.payload.orders),
        )
