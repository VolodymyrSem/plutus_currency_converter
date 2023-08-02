import colorama
from datetime import datetime

from converter.core.currency_converter import CurrencyPair


class Menu:
    menu_options = {
        '1': 'Exchange calculator',
        '2': 'Make a payment with a conversion',
        '3': 'Show rates for saved currencies',
        '4': 'Refresh your database',
        '5': 'Create new pairs of saved currencies',
        '6': 'Delete pair from saved currencies',
        '7': 'Delete ALL pairs from saved currencies',
        '0': 'Exit'
    }

    output_style = colorama.Back.WHITE + colorama.Fore.BLACK + colorama.Style.DIM
    error_style = colorama.Fore.RED

    def __init__(self):
        colorama.init(autoreset=True)

    def print_main_menu(self):
        self.__print_header()
        self.__print_menu_options()

    def __print_header(self):
        print('+' + '-' * 30 + '+')
        print('|' + 'CURRENCY CONVERTER'.center(30) + '|')
        print('+' + '-' * 30 + '+')
        print('Choose an action you want to do:\n')

    def __print_menu_options(self):
        print('x. Switch rates\' source (actual rates by default)\n')
        for key, value in self.menu_options.items():
            print(key + '. ' + value)

    def input_choice_main_menu(self):
        while True:
            input_choice = input('\nType your choice (0...7 or x): ').strip()
            if input_choice in ['1', '2', '3', '4', '5', '6', '7', '0', 'x']:
                return input_choice
            else:
                self.print_bad_choice_error()

    def print_exchange_result(self, currency_pair: CurrencyPair):
        costs_or_cost = 'costs' if currency_pair.amount == 1 else 'cost'
        print()
        print(self.output_style + '~' * 50)
        print(self.output_style + f'{currency_pair.amount} '
                             f'{currency_pair.from_currency} '
                             f'{costs_or_cost} '
                             f'{currency_pair.result:.2f} '
                             f'{currency_pair.to_currency}'.center(50))
        print(self.output_style + '~' * 50)

    def print_double_conversion_result(self, currency_pair: CurrencyPair):
        print()
        print(self.output_style + '~' * 50)
        print(self.output_style + f'You need to pay '
                             f'{currency_pair.result:.2f} '
                             f'{currency_pair.from_currency} for '
                             f'{currency_pair.amount:.0f} '
                             f'{currency_pair.to_currency}'.center(50))
        print(self.output_style + '~' * 50)

    def print_success_switch_source(self, from_db: bool):
        source = 'saved' if from_db else 'actual'
        self.print_smth_successfully('Switched the mode to %s rates' % source)

    def print_smth_successfully(self, first_part: str):
        print(f'\n{first_part} successfully!')

    def ask_accepting_for_creating_db_now(self):
        print('\nIt seems, that you haven\'t got needed database yet.\n'
              'Do you want to create one now? It will take approx. 3-5 minutes.\n'
              'If not, you may continue by switching the mode to actual rate further.\n')

    def ask_accepting_to_delete_all_pairs(self):
        print('\nAre you sure to delete ALL pairs?\n')

    def user_accepted(self) -> bool:
        answer = input('Accept by typing y (anything else to cancel): ')
        if answer.strip() == 'y':
            return True
        else:
            return False

    def print_updating_database(self):
        print('\nPlease, wait. Updating your database... It will take a few minutes\n')

    def print_input_error(self):
        message = 'Bad input. Repeat, please.'
        self.__print_error(message)

    def print_bad_choice_error(self):
        message = 'There isn\'t the option. Repeat your choice, please.'
        self.__print_error(message)

    def print_pair_not_found_error(self):
        message = 'Can\'t find provided pair. Repeat your input, please.'
        self.__print_error(message)

    def print_exception(self, e: Exception):
        message = e.__str__()
        self.__print_error(message)

    def __print_error(self, message: str):
        print(self.error_style + '\n' + message)

    def print_exiting(self):
        print('\nExiting...')

    def input_exchange(self) -> list:
        return input(
            self.__string_for_pair_input_with_format('100 USD EUR or USD EUR')
        ).split()

    def input_double_conversion(self) -> list:
        return input(
            self.__string_for_pair_input_with_format('USD 100 EUR VISA')
        ).split()

    def input_delete_pair(self) -> list:
        return input(
            self.__string_for_pair_input_with_format('USD EUR')
        ).split()

    def __string_for_pair_input_with_format(self, format: str):
        return f'\nWrite a line in a format {format} \n<nothing to cancel>:\n'

    def progress_bar(self, progress: int, total: int):
        percent = 100 * (progress / total)
        count = int(percent // 2)
        bar = '█' * count + '■' * (50 - count)
        print(colorama.Fore.YELLOW + f'\r|{bar}| {percent:.2f}%', end='\r')
        if progress == total:
            print(colorama.Fore.GREEN + f'\r|{bar}| {percent:.2f}%')

    def print_when_database_was_updated(self, timestamp: float):
        if timestamp:
            time_updated = datetime.fromtimestamp(timestamp)
            time_updated = time_updated.strftime('%H:%M %d.%m.%Y')
        else:
            time_updated = 'never'
        print(f'\nLast time database was updated at {time_updated}')

    def ask_to_continue(self):
        input('\nContinue?\n(Press return)\n')

    def print_goodbye(self):
        print('\nThank you for using the application. Goodbye!')