import os
import sqlite3 as sql

from converter.core.exceptions import (
    DatabaseNotExistError,
    EmptySavedPairsTableException,
    NoSuchPairException
)
from converter.db import queries


class DBHandler:

    def __init__(self):
        self.connect, self.c = self.__connect_to_db()

    def __connect_to_db(self) -> sql.Connection | sql.Cursor:
        connect = sql.connect(self.get_path_to_db(), check_same_thread=False)
        c = connect.cursor()
        return (connect, c)

    def get_path_to_db(self) -> str:
        return os.path.abspath('data\\rates.db')

    def prepared_currencies_exist_and_complete(self) -> bool:
        self.db_file_exists()
        if self.get_last_pair_id() == 26082:
            return True
        return False

    def get_last_pair_id(self):
        self.c.execute(
            queries.GET_LAST_PAIR_FROM_PREPARED_CURRENCIES
        )
        return self.c.fetchone()[0]

    def db_file_exists(self):
        if not 'rates.db' in os.listdir('data'):
            raise DatabaseNotExistError

    def get_rate_from_db(self, currencies: tuple) -> float:
        self.c.execute(
            queries.GET_RATE,
            currencies
        )
        return self.c.fetchone()[0]

    def get_saved_currencies(self) -> list:
        pairs = self.c.execute(queries.GET_SAVED_CURRENCIES).fetchall()
        if pairs:
            return pairs
        else:
            raise EmptySavedPairsTableException

    def insert_pair_in_prepared_currencies(self, tuple_to_insert: tuple):
        self.c.execute(
            queries.INSERT_PAIR_IN_PREPARED_CURRENCIES,
            tuple_to_insert
        )
        self.connect.commit()

    def insert_new_pair_in_saved_currencies(self, currencies_with_amount: tuple):
        self.c.execute(
            queries.INSERT_NEW_PAIR_IN_SAVED_CURRENCIES,
            currencies_with_amount
        )
        self.connect.commit()

    def create_table_saved_currencies(self):
        self.c.execute(
            queries.CREATE_TABLE_SAVED_CURRENCIES
        )

    def create_table_prepared_currencies(self):
        self.c.execute(
            queries.CREATE_TABLE_PREPARED_CURRENCIES
        )
        self.connect.commit()

    def try_delete_saved_pair(self, currencies: tuple):
        self.get_pair_from_saved_currencies(currencies)
        self.c.execute(
            queries.DELETE_PAIR_FROM_SAVED_CURRENCIES,
            currencies
        )
        self.connect.commit()

    def get_pair_from_saved_currencies(self, currencies: tuple) -> tuple:
        pair = self.c.execute(
            queries.GET_PAIR_FROM_SAVED_CURRENCIES,
            currencies
        ).fetchone()
        if pair is not None:
            return pair
        else:
            raise NoSuchPairException

    def delete_all_from_prepared_currencies(self):
        self.c.execute(
            queries.DELETE_ALL_FROM_PREPARED_CURRENCIES
        )
        self.connect.commit()

    def delete_all_from_saved_currencies(self):
        self.c.execute(
            queries.DELETE_ALL_FROM_SAVED_CURRENCIES
        )
        self.connect.commit()

