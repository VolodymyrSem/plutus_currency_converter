import os
from collections import deque

from converter.core.currency_pair import CurrencyPair

from converter.core.double_conversion import CurrencyConverterDoubleConversion
from converter.core.exceptions import *
from converter.handlers.main_handler import MainHandler
from converter.app.menu import Menu


class App:
    """

    """

    def __init__(self):
        self.converter = CurrencyConverterDoubleConversion()
        self.menu = Menu()
        self.handler = MainHandler()

    def exchange(self):
        """
        Requests names of owned currency, target currency and amount of the operation, validates the data
        """

        if self.__input_is_ready_to_exchange():
            if self.converter.rates_are_from_db:
                self.__check_db_and_update_if_needed()
            self.converter.exchange()
            self.menu.print_exchange_result(self.converter.currency_pair)
            self.converter.currency_pair = None

    def create_pairs(self):
        """
        Requests names of owned currency, target currency and amount of the operation, validates the data.
        """

        while True:
            if self.__input_is_ready_to_exchange():
                self.handler.db.insert_new_pair_in_saved_currencies(
                    self.converter.currency_pair.get_pair_as_tuple()
                )
                self.menu.print_smth_successfully('Inserted pair')
                self.converter.currency_pair = None
            else:
                return

    def __input_is_ready_to_exchange(self) -> bool:
        while True:
            input_data = self.menu.input_exchange()
            if not input_data:
                return False
            elif len(input_data) == 2:
                from_currency, to_currency = input_data
                self.converter.currency_pair = CurrencyPair(
                    from_currency, to_currency, 1
                )
            elif len(input_data) == 3:
                amount, from_currency, to_currency = input_data
                if self.__amount_valid(amount):
                    self.converter.currency_pair = CurrencyPair(
                        from_currency, to_currency, float(amount)
                    )

            if self.__input_currencies_valid():
                return True

            self.converter.currency_pair = None
            self.menu.print_input_error()

    def double_conversion(self):
        """
        Requests names of owned currency, target currency, amount of the operation and a card system used,
        validates the data, passes it to CurrencyConverter.double_conversion method for processing.
        Outputs the result using App.menu method.
        """

        if self.__input_is_ready_to_double_conv():
            if self.converter.rates_are_from_db:
                self.__check_db_and_update_if_needed()
            self.converter.double_conversion()
            self.menu.print_double_conversion_result(self.converter.currency_pair)
            self.converter.currency_pair = None

    def __input_is_ready_to_double_conv(self):
        while True:
            input_data = self.menu.input_double_conversion()
            if not input_data:
                return False
            elif len(input_data) == 4:
                from_currency, amount, to_currency, card_type = input_data
                card_type = card_type.upper()
                if (
                        self.__amount_valid(amount) and
                        self.__card_type_valid(card_type)
                ):
                    self.converter.currency_pair = CurrencyPair(
                        from_currency,
                        to_currency,
                        float(amount),
                        card_type
                    )

            if self.__input_currencies_valid():
                return True

            self.converter.currency_pair = None
            self.menu.print_input_error()

    def __amount_valid(self, amount: str) -> bool:
        return amount.isdigit()

    def __card_type_valid(self, card_type: str) -> bool:
        return card_type in ['MC', 'VISA']

    def __input_currencies_valid(self) -> bool:
        """
        Checks if the provided input with names of currencies is valid.
        """

        if (
                self.converter.currency_pair is not None and
                self.converter.currency_pair.currencies_filled_out()
        ):
            return True
        return False

    def show_saved_currencies(self):
        """
        Requests records from CurrencyConverter.show_saved_currencies method to process them.
        While processing all pairs, shows progress bar from Utilities.progress_bar method.
        Outputs the results using App.menu method.
        """
        try:
            data = self.handler.db.get_saved_currencies()

            if self.converter.rates_are_from_db:
                self.__check_db_and_update_if_needed()

            queue = deque([])

            progress = 0
            total = len(data)
            for from_currency, to_currency, amount in data:
                currency_pair = self.converter.exchange(
                    CurrencyPair(from_currency, to_currency, amount)
                )
                queue.appendleft(currency_pair)

                progress += 1
                self.menu.progress_bar(progress, total)

            while queue:
                self.menu.print_exchange_result(queue.pop())
        except EmptySavedPairsTableException as e:
            self.menu.print_exception(e)
            return

    def __check_db_and_update_if_needed(self):
        try:
            self.handler.db.prepared_currencies_exist_and_complete()
        except DatabaseNotExistError:
            self.__update_rates_or_switch_rate_source()

    def __update_rates_or_switch_rate_source(self):
        if self.__user_wants_to_update_db_now():
            self.handler.update_rates()
        else:
            self.switch_rate_source()

    def __user_wants_to_update_db_now(self):
        self.menu.ask_accepting_for_creating_db_now()
        return self.menu.user_accepted()

    def update_rates(self):
        self.handler.update_rates()

    def switch_rate_source(self):
        self.converter.switch_rate_source()
        self.menu.print_success_switch_source(self.converter.rates_are_from_db)
        if self.converter.rates_are_from_db:
            timestamp = self.handler.timestamp_when_database_was_last_time_updated()
            self.menu.print_when_database_was_updated(timestamp)

    def delete_pairs(self):
        """
        Requests names of owned currency, target currency and amount of the operation, validates the data, passes
        it to CurrencyConverter.delete_pai method for deleting the pair from the database's table 'saved_currencies'.
        """

        while True:
            try:
                input_data = self.menu.input_delete_pair()
                if not input_data:
                    break
                elif len(input_data) == 2:
                    from_currency, to_currency = input_data
                    self.converter.currency_pair = CurrencyPair(
                        from_currency,
                        to_currency
                    )
                    self.handler.db.try_delete_saved_pair(
                        self.converter.currency_pair.get_pair_as_tuple()[:2]
                    )
                    self.menu.print_smth_successfully('Deleted pair')
                else:
                    self.menu.print_input_error()
            except NoSuchPairException:
                self.menu.print_pair_not_found_error()

    def delete_all_pairs(self):
        """Requests from the user accepting of deleting all records from the database's table 'saved_currencies'"""

        self.menu.ask_accepting_to_delete_all_pairs()
        if self.menu.user_accepted():
            self.handler.db.delete_all_from_saved_currencies()
            self.menu.print_smth_successfully('Deleted all pairs')

    def set_up_directories_and_check_server_state(self):
        self.handler.api.check_server_state()

        if 'converter' not in os.listdir():
            os.chdir('../..')

        if not os.path.exists('data'):
            os.mkdir('data')
