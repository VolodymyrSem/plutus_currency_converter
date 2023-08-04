import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from converter.app.menu import Menu
from converter.handlers.API import APIHandler
from converter.handlers.backup import BackupJSONFileHandler
from converter.db.db import DBHandler


class MainHandler:
    def __init__(self):
        self.backup = BackupJSONFileHandler()
        self.api = APIHandler()
        self.db = DBHandler()
        self.menu = Menu()

    def update_rates(self):
        """
        Updates rates for all predefined pairs of currencies
        """

        backup_data = self.api.get_rates_from_API()
        self.backup.rewrite_backup(backup_data)

        list_of_currencies = self.api.get_list_of_currencies()
        self.__setup_multi_threading(list_of_currencies)

        self.__update_pairs_in_prepared_currencies()

    def __setup_multi_threading(self, list_of_currencies: list[str]):
        setattr(self, 'currencies_to_get_rates', list_of_currencies)
        setattr(self, 'done_records', 0)
        setattr(self, 'pipeline', Queue(maxsize=10))
        setattr(self, 'event', threading.Event())

    def __update_pairs_in_prepared_currencies(self):
        self.db.delete_all_from_prepared_currencies()
        self.db.connect.commit()

        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(self.__get_rates_and_update_pipeline)
            executor.submit(self.__put_rates_to_db)

        self.menu.print_smth_successfully('Updated database')

    def __get_rates_and_update_pipeline(self):
        while self.currencies_to_get_rates:
            from_currency = self.currencies_to_get_rates.pop()
            rates = self.api.get_rates_from_API(from_currency)
            self.pipeline.put((from_currency, rates))
        self.event.set()

    def __put_rates_to_db(self):
        while not self.pipeline.empty() or not self.event.is_set():
            result = self.pipeline.get() if not self.pipeline.empty() else None
            if result is not None:
                self.__put_pairs_to_db(result)

    def __put_pairs_to_db(self, from_currency_and_results: tuple):
        from_currency, rates = from_currency_and_results
        for to_currency, rate in list(rates.items())[1:]:
            tuple_to_insert = (from_currency, to_currency, rate)

            self.db.insert_pair_in_prepared_currencies(tuple_to_insert)

            self.done_records += 1
            self.menu.progress_bar(self.done_records, 26082)

    def timestamp_when_database_was_last_time_updated(self):
        return self.backup.get_timestamp_from_backup()
