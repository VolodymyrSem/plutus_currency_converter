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
        Updates rates for all predefined pairs of currencies'
        """

        backup_data = self.api.get_rates_from_api()
        list_of_currencies = self.api.get_list_of_currencies()
        self.backup.rewrite_backup(backup_data)
        self.__update_pairs_in_prepared_currencies(list_of_currencies)

    def __update_pairs_in_prepared_currencies(self, list_of_currencies: list[str]):
        self.db.delete_all_from_prepared_currencies()
        self.db.connect.commit()

        number_of_currencies = len(list_of_currencies)

        progress = 0
        total = number_of_currencies * (number_of_currencies - 1)

        self.menu.progress_bar(progress, total)

        for from_currency in list_of_currencies:
            rates = self.api.get_rates_from_api(from_currency)
            for target_currency, result in list(rates.items())[1:]:
                tuple_to_insert = (from_currency, target_currency, result)
                self.db.insert_pair_in_prepared_currencies(tuple_to_insert)

                progress += 1
                self.menu.progress_bar(progress, total)

        self.menu.print_smth_successfully('Updated database')

    def timestamp_when_database_was_last_time_updated(self):
        return self.backup.get_timestamp_from_backup()
