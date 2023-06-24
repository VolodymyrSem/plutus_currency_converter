import requests
import re
import time
import sqlite3 as sql
import colorama
import os
import pandas as pd
import urllib
import currencyapicom
import json


class ExchangeError(BaseException):
    '''Class for exception used in the program'''

    pass


class Utilities:
    """
    Class containing progress bar and switch for source of rates.
    Used for decorations of execution of the program in terminal.

    Parameters
    ----------
    switch : bool
        switches the mode for source of rates used in outputs. Default value: True

    Methods
    -------
    progress_bar(progress, total, color=colorama.Fore.YELLOW)
        Prints the progress bar using the provided color.
    switch_rate_source()
        Switches source of rates used in outputs.
    """

    switch = True

    def progress_bar(self, progress, total, color=colorama.Fore.YELLOW):
        """Prints the progress bar

        Parameters
        ----------
        progress : int
            actual progress of the progress bar
        total : int
            total amount of calls needed to finish the progress bar
        color : colorama.ansi.AnsiFore, optional
            color in which the progress bar is repainted
        """

        percent = 100 * (progress / total)
        count = int(percent // 2)
        bar = '█' * count + '■' * (50 - count)
        print(color + f'\r|{bar}| {percent:.2f}%', end='\r')
        if progress == total:
            print(colorama.Fore.GREEN + f'\r|{bar}| {percent:.2f}%', end='\r')

    def switch_rate_source(self):
        """Switches source of rates used in outputs.

        Possible sources:
        API and prepared pairs of currencies in the internal database's table 'prepared_currencies',
        downloaded after user's accepting.

        The program works much more efficiently while using internal database,
        thus it takes up to 5 minutes to 'exchange' all currencies.
        """

        self.menu(4)
        answer = input('Write 1 or 2: ')
        while True:
            if answer == '1':
                self.switch = True
                print('\nSwitched the mode to actual rates successfully!')
                return
            elif answer == '2':
                self.switch = False
                print('\nSwitched the mode to saved rates successfully!')
                return
            else:
                self.menu(5)


class CurrencyConverter(Utilities):
    """
    Superclass: Utilities, used to have access to progress_bar method
    Contains methods for getting and computing results of user's request.

    Methods
    -------
    exchange(from_currency, to_currency, amount=1)
        Returns rate for requested pair of currencies, source of the rate depends on state of the switch at that moment.
    double_conversion(from_currency, to_currency, card_type, amount=1)
        Returns amount to pay for amount of the target currency.
        Uses predefined algorithms for computing result due to the issues
        with a possibility of double/triple conversion rate by card systems.
    update_rates()
        Updates rates for pairs of currencies in the internal database's table 'prepared_currencies'.
    show_saved_currencies()
        Returns rates for currencies for predefined by user pairs.
    add_new_pair(from_currency, to_currency, amount):
        Creates new pairs of currencies in the database's table 'saved_currencies' by user's input.
    delete_pair(from_currency, to_currency)
        Deletes predefined pair from the database's table 'saved_currencies'.
    delete_all()
        Deletes all pairs from the database's table 'saved_currencies'.
    """

    def __init__(self):
        """
        Raises
        ------
        ExchangeError
            In case of a bad response from the API
        """
        if not os.path.exists('data'):
            os.mkdir('data')
        self.response = requests.get(TARGET_URL)
        if not self.response:
            raise ExchangeError('Bad connection with the server.')
        self.connect = sql.connect(BASE_DIR + '/data/rates.db')
        self.c = self.connect.cursor()
        self.c.execute('''
                CREATE TABLE IF NOT EXISTS saved_currencies (
                id INTEGER PRIMARY KEY,
                from_currency STRING,
                to_currency STRING,
                amount INTEGER,
                UNIQUE(from_currency, to_currency)
                )''')

    def exchange(self, from_currency: str, to_currency: str, amount=1) -> float:
        """
        Returns rate for a pair of currencies.
        Method is used by other methods in exchanging purposes.
        Source of rates may be switched between API and internal database's table 'prepared_currencies'.

        Parameters
        ----------
        from_currency : str
            currency provided as currency to be exchanged by another one; owned currency
        to_currency : str
            target currency
        amount : int, optional
            amount of the owned currency

        Raises
        ------
        ExchangeError
            Raises in cases of not presence of the internal database's table 'prepared_currencies' (or it's emptiness),
            issues with callback from the API and as a base case for all other exceptions.
        """

        try:
            if not self.switch:
                if 'rates.db' not in os.listdir(BASE_DIR + '/data'):
                    print('It seems, that you haven\'t got needed database yet. ' + \
                          'Do you want to create one now? It will take approx. 3-5 minutes. ' + \
                          'If not, you may continue by switching the mode to actual rate further.')
                    if self.menu(6):
                        self.update_rates()
                    else:
                        super().switch_rate_source()
                        return
                self.c.execute('''
                      SELECT (rate) FROM prepared_currencies
                      WHERE from_currency = ?
                      AND to_currency = ?''', (from_currency, to_currency))

                rate = self.c.fetchone()[0]
                data = rate * amount

            else:
                post = requests.get(TARGET_URL + \
                                         f'?from={from_currency}' + \
                                         f'&to={to_currency}' + \
                                         f'&amount={amount}')
                # print(post.text)
                data = re.search(r'<span class="ccOutputRslt">([\d,]+.\d*)<span class', post.text)
                data = data.group(1).replace(',', '')
            return float(data)
        except AttributeError:
            raise ExchangeError('\nBad connection with the server.')
        except (sql.OperationalError, TypeError):
            raise ExchangeError('Your database is empty or doesn\'t exist.' + \
                                 '\nRestart the program and choose "Refresh your database".')
        except:
            raise ExchangeError('\nUnexpected error occurred.')

    def double_conversion(self, from_currency: str, to_currency: str, card_type: str, amount=1) -> float:
        """
        Returns amount of an owned currency needed to pay for amount of a target currency.
        Result depends on a card system, which may have a consequence of double/triple conversion.
        Uses CurrencyConverter.exchange method as a base method for exchanging currencies.

        Parameters
        ----------
        from_currency : str
            currency provided as currency to be exchanged by another one; owned currency
        to_currency : str
            target currency
        card_type : str
            card system for the operation. May be 'MC' or 'VISA'
        amount : int, optional
            amount of the owned currency
        """

        if card_type == 'MC' and to_currency not in EUROPE_CURRENCIES['AlphabeticCode'].unique():
            if from_currency == 'EUR':
                dc_from_EUR = amount
            else:
                dc_from_EUR = (amount / self.exchange('EUR', to_currency)) * 1.02
            result = (dc_from_EUR / self.exchange(from_currency, 'EUR')) * 1.02

        elif card_type == 'MC':
            price = self.exchange(from_currency, to_currency)
            result = (amount / price) * 1.02

        elif card_type == 'VISA' and to_currency in EUROPE_CURRENCIES['AlphabeticCode'].unique():
            if to_currency != 'EUR':
                dc_from_EUR = (amount / self.exchange('EUR', to_currency)) * 1.03
            else:
                dc_from_EUR = amount
            dc_from_USD = (dc_from_EUR / self.exchange('USD', 'EUR')) * 1.03
            if from_currency != 'USD':
                result = (dc_from_USD / self.exchange(from_currency, 'USD')) * 1.03
            else:
                result = dc_from_USD

        elif card_type == 'VISA':
            if to_currency != 'USD':
                dc_from_USD = (amount / self.exchange('USD', to_currency)) * 1.03
            else:
                dc_from_USD = amount
            if from_currency != 'USD':
                result = (dc_from_USD / self.exchange(from_currency, 'USD')) * 1.03
            else:
                result = dc_from_USD

        return round(float(result), 2)

    def update_rates(self):
        """
        Updates rates for all predefined pairs of currencies in database's table 'prepared currencies'.
        However, it is recommended to update rates once a day, may be updated after confirming at any time.
        Creates or opens text file timestamp.txt to find out when the db was updated for the last time,
        therefor changing this value to the actual timestamp.
        Method uses Utilities.progress_bar method to show the progress.
        """

        timestamp = time.time()

        if 'timestamp.txt' not in os.listdir(BASE_DIR + '/data'):
            with open(BASE_DIR + '/data/timestamp.txt', 'w') as file:
                file.write(str(timestamp))
        else:
            with open(BASE_DIR + '/data/timestamp.txt', 'r+') as file:
                if (timestamp - float(file.readline()) < 86400 and
                    'rates.db' in os.listdir(BASE_DIR + '/data')):
                    print('It is no need to refresh your database, data is actual.\n')
                    return
                file.seek(0)
                file.truncate()
                file.write(str(timestamp))

        print('\nPlease, wait. Updating your database... It will take a few minutes\n')

        self.c.execute('''
                      CREATE TABLE IF NOT EXISTS prepared_currencies (
                      id INTEGER PRIMARY KEY,
                      from_currency STRING,
                      to_currency STRING,
                      rate REAL,
                      UNIQUE(from_currency, to_currency)
                      )''')
        self.c.execute('DELETE FROM prepared_currencies')
        self.connect.commit()

        # download 'USD - X' pairs from the API
        api_object = currencyapicom.Client(API_KEY)
        rates_from_usd = api_object.latest(
            base_currency='USD',
            currencies=[currency for currency in CURRENCIES_SHORT['AlphabeticCode']])

        total = len(rates_from_usd['data']) * (len(rates_from_usd['data']) + 1)
        progress = 0

        self.progress_bar(progress, total)
        for base_currency in rates_from_usd['data'].items():
            for target_currency in rates_from_usd['data'].items():
                if base_currency[0] == target_currency[0]:
                    continue

                rate = round(target_currency[1]['value'] / base_currency[1]['value'], 5)

                self.c.execute(
                    '''INSERT INTO prepared_currencies (from_currency, to_currency, rate)
                      VALUES (?, ?, ?)''', (base_currency[0], target_currency[0], rate)
                )
                self.connect.commit()
                self.progress_bar(progress, total)

        # pass to progress bar numbers to have 100% completion
        # in case of wrong calculation of the total amount of iterations
        self.progress_bar(1, 1)

        self.switch = False

    def show_saved_currencies(self):
        """
        Downloads all records of saved currencies' pairs in the database's table 'saved_currencies'
        to process them further and to output rates for them.
        """

        data = self.c.execute('SELECT from_currency, to_currency, amount FROM saved_currencies').fetchall()
        if data:
            return data
        else:
            print('Can\'t find any saved pairs of currencies. Create them first, please.\n')

    def add_new_pair(self, from_currency: str, to_currency: str, amount: float):
        """Adds a new record in the database's table 'saved_currencies'"""

        self.c.execute('''
                INSERT OR IGNORE INTO saved_currencies (from_currency, to_currency, amount)
                VALUES (?, ?, ?)''', (from_currency, to_currency, amount))
        self.connect.commit()
        print('\nAdded pair successfully!')

    def delete_pair(self, from_currency: str, to_currency: str):
        """Deletes a pair of currencies from the database's table 'saved_currencies'"""

        self.c.execute('''
                DELETE FROM saved_currencies 
                WHERE from_currency=(?)
                AND to_currency=(?)
                ''', (from_currency, to_currency))
        self.connect.commit()
        print('\nDeleted pair successfully!')

    def delete_all(self):
        """Deletes every single pair of currencies from the database's table 'saved_currencies'"""

        self.c.execute('DELETE FROM saved_currencies')
        self.connect.commit()
        print('\nDeleted pairs successfully!')


class App(CurrencyConverter):
    """
    Superclass: CurrencyConverter, uses this class as a backend of the program.
    The class defined mainly to:
    - request inputs
    - check their correctness
    - provide outputs
    - communicate with the user

    Methods
    -------
    menu(switch=0, from_currency='', to_currency='', amount='', result='')
        Outputs the results and errors in user-friendly way.
    valid_input(from_currency, to_currency, amount=0, card_type='MC')
        Checks if inputted words are valid to process them further.
    input_choice()
        Checks if an inputted choice in the main menu is valid.
    app_exchange()
        Frontend part of CurrencyConverter.exchange method,
        is used to request an input of pair of currencies and amount of the operation, checks if the input is valid,
        passes data further to backend method
    app_double_conversion()
        Frontend part of CurrencyConverter.double_conversion method,
        is used to request an input of pair of currencies and amount of the operation, checks if the input is valid,
        passes data further to backend method
    app_show_saved_currencies()
        Frontend part of CurrencyConverter.show_saved_currencies method,
        is used to process every pair of currencies in the database's table 'saved_currencies' in form of passing them
        to CurrencyConverter.exchange method and outputting the results.
    app_create_pairs()
        Frontend part of CurrencyConverter.add_new_pair method,
        requests from the user pairs and pass them to the backend method.
    app_delete_pairs()
        Frontend part of CurrencyConverter.delete_pair method,
        requests from the user pairs and pass them to the backend method.
    app_delete_all()
        Frontend part of CurrencyConverter.delete_all method,
        requests from the user accepting of deleting all records from the database's table 'saved_currencies'.
    """

    def __init__(self):
        super().__init__()

    def menu(self, switch=0, from_currency='', to_currency='', amount='', result='') -> bool:
        """
        Gathers all forms of possible communication messages with the user and
        outputs of processed requests in user-friendly way.
        Uses different colors for an ordinary output and an error message.

        Parameters
        ----------
        switch : int, optional
            changes output form which will be used
        from_currency : str, optional
            currency provided as currency to be exchanged by another one; owned currency
        to_currency : str, optional
            target currency
        amount : int, optional
            amount of the owned currency
        result : str, optional
            result of the exchange
        """

        output_style = colorama.Back.WHITE + colorama.Fore.BLACK + colorama.Style.DIM
        error = colorama.Fore.RED

        if not switch:
            print('+' + '-' * 30 + '+')
            print('|' + 'CURRENCY CONVERTER'.center(30) + '|')
            print('+' + '-' * 30 + '+')
            print(
'''
Choose the action you want to make:

x. Switch rates\' source (actual by default)

1. Exchange calculator
2. Make a payment with a conversion
3. Show rate for saved currencies
4. Refresh your database if needed
5. Create new pairs of saved currencies
6. Delete pair from saved currencies
7. Delete ALL pairs from saved currencies
0. Exit
''')
        elif switch == 1:
            print(error + '\nBad input. Repeat, please.')

        elif switch == 2:
            print()
            cost = 'costs' if amount == 1 else 'cost'
            print('\n' + output_style + '~' * 50)
            print(output_style + f'{amount} {from_currency} {cost} {result} {to_currency}'.center(50))
            print(output_style + '~' * 50)

        elif switch == 3:
            print('\n' + output_style + '~' * 50)
            print(output_style + f'You need to pay {result} {from_currency} for {amount} {to_currency}'.center(50))
            print(output_style + '~' * 50)

        elif switch == 4:
            print(
'''
Choose whether you need rates for this moment or not:

1. For this moment
2. Recently saved
''')

        elif switch == 5:
            print(error + '\nThere isn\'t the option. Repeat your choice, please.\n')

        elif switch == 6:
            answer = input('\nAccept by typing y (anything else to cancel): ')
            if answer == 'y':
                return True
            else:
                return False

    def valid_input(self, from_currency: str, to_currency: str, amount=0, card_type='MC') -> tuple:
        """
        Checks if the provided input of names of currencies, amount of the operation and card type are valid.
        Has a search algorithm in case of using first letters of a name of a country to find out a name of currencies.
        Returns a tuple (owned currency name, target currency name) or None in case of bad input.

        Parameters
        ----------
        from_currency : str, optional
            currency provided as currency to be exchanged by another one; owned currency
        to_currency : str, optional
            target currency
        amount : int, optional
            amount of the owned currency
        card_type : str, optional
            card system for the operation. May be 'MC' or 'VISA'
        """

        from_currency = trie_object.search(from_currency)
        to_currency = trie_object.search(to_currency)
        if (from_currency and
                to_currency and
                amount.isdigit() and
                card_type in ['MC', 'VISA']):
            if from_currency.islower():
                from_currency = trie_object.currencies_dict[from_currency]
            if to_currency.islower():
                to_currency = trie_object.currencies_dict[to_currency]
            return (from_currency, to_currency)
        return None

    def input_choice(self):
        """Checks if the choice in the main menu is valid"""

        while True:
            input_num = input('Write a number (0...7 or x): ').strip()
            if input_num in ['1', '2', '3', '4', '5', '6', '7', '0', 'x']:
                return input_num
            else:
                self.menu(5)

    def app_exchange(self):
        """
        Requests names of owned currency, target currency and amount of the operation, validates the data, passes
        it to CurrencyConverter.exchange method for processing. Outputs the result using App.menu method.
        """

        while True:
            input_data = input('\nWrite a line in a format "100 USD EUR" or "USD EUR"\n<nothing to cancel>:\n').split()
            if len(input_data) == 2:
                from_currency, to_currency = input_data
                amount = '1'
            elif len(input_data) == 3:
                amount, from_currency, to_currency = input_data
            elif input_data == []:
                return
            else:
                self.menu(1)
                continue

            check = self.valid_input(from_currency, to_currency, amount)
            if not check:
                self.menu(1)
                continue
            else:
                from_currency, to_currency = check
            data = super().exchange(from_currency, to_currency, float(amount))
            self.menu(2, from_currency, to_currency, amount, f'{data:,.2f}')
            return

    def app_double_conversion(self):
        """
        Requests names of owned currency, target currency, amount of the operation and a card system used,
        validates the data, passes it to CurrencyConverter.double_conversion method for processing.
        Outputs the result using App.menu method.
        """

        while True:
            input_data = input('\nWrite a line in a format "USD 100 EUR VISA"\n<nothing to cancel>:\n').split()
            if len(input_data) == 4:
                from_currency, amount, to_currency, card_type = input_data
                card_type = card_type.upper()
            elif input_data == []:
                return
            else:
                self.menu(1)
                continue

            check = self.valid_input(from_currency, to_currency, amount, card_type)
            if not check:
                self.menu(1)
                continue
            else:
                from_currency, to_currency = check

            data = super().double_conversion(from_currency, to_currency, card_type, float(amount))
            self.menu(3, from_currency, to_currency, amount, f'{data:,.2f}')
            return

    def app_show_saved_currencies(self):
        """
        Requests records from CurrencyConverter.show_saved_currencies method to process them.
        While processing all pairs, shows progress bar from Utilities.progress_bar method.
        Outputs the results using App.menu method.
        """

        data = super().show_saved_currencies()
        if data:
            print()
            self.progress_bar(0, len(data))
            results = []
            for index, pair in enumerate(data):
                result = "%.2f" % self.exchange(pair[0], pair[1], pair[2])
                results.append((pair[0], pair[1], pair[2], result))
                self.progress_bar(index + 1, len(data))
            print(colorama.Fore.RESET)
            for result in results:
                self.menu(2, result[0], result[1], result[2], result[3])
            results.clear()
        else:
            return

    def app_create_pairs(self):
        """
        Requests names of owned currency, target currency and amount of the operation, validates the data, passes
        it to CurrencyConverter.add_new_pair method for adding to the database's table 'saved_currencies'.
        """

        while True:
            input_data = input('\nWrite a line in a format "100 USD EUR" or "USD EUR"\n<nothing to exit>:\n').split()
            if len(input_data) == 2:
                from_currency, to_currency = input_data
                amount = '1'
            elif len(input_data) == 3:
                amount, from_currency, to_currency = input_data
            elif input_data == []:
                return
            else:
                self.menu(1)
                continue

            check = self.valid_input(from_currency, to_currency, amount)
            if not check:
                self.menu(1)
                continue
            else:
                from_currency, to_currency = check
            super().add_new_pair(from_currency, to_currency, amount)

    def app_delete_pairs(self):
        """
        Requests names of owned currency, target currency and amount of the operation, validates the data, passes
        it to CurrencyConverter.delete_pai method for deleting the pair from the database's table 'saved_currencies'.
        """

        while True:
            input_data = input('\nWrite a line in a format "USD EUR"\n<nothing to exit>:\n').split()
            if len(input_data) == 2:
                from_currency, to_currency = input_data
            elif input_data == []:
                return
            else:
                self.menu(1)
                continue

            super().delete_pair(from_currency, to_currency)

    def app_delete_all(self):
        """Requests from the user accepting of deleting all records from the database's table 'saved_currencies'"""

        answer = input('\nAre you sure to delete ALL pairs? ')
        if answer.lower().strip() in ['y', 'yes', 'sure']:
            super().delete_all()


class TrieNode:
    """
    Node of the trie, used to store one letter of processed words.
    Connects letter with further ones using set 'self.children'.
    Stores if the letter is an end of some word in a variable 'self.end'.
    """

    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    """
    Prefix tree that stores names of currencies and countries. Used to validate inputted currencies and
    to provide a search with the first 3 letters of a country's name.
    Lowercase words are countries, uppercase words are currency codes.
    self.currencies_dict -> {country name : alphabetic currency code}

    Methods
    -------
    add_word(word)
        Adds a new word to the trie
    search(prefix)
        Searches a word with a given prefix, returns the word
    """

    def __init__(self):
        self.root = TrieNode()
        self.currencies_dict = {}

    def add_word(self, word: str):
        """
        Adds a new word to the trie.
        Iterates through letters, adds letter to the previous one's children set.

        Parameters
        ----------
        word : str
            word to add to the trie
        """

        curr = self.root

        for c in word:
            if c not in curr.children:
                curr.children[c] = TrieNode()
            curr = curr.children[c]

        curr.end = True

    def search(self, prefix: str) -> str:
        """
        Searches a word with a given prefix among all added before words.
        Returns the word or None in case of non-existence of such word.

        Parameters
        ----------
        prefix : str
            prefix to search the word with; lowercase -> country's name, uppercase -> currency code
        """
        curr = self.root
        answer = ''

        for c in prefix:
            if c not in curr.children:
                return ''
            answer += c
            curr = curr.children[c]

        while not curr.end:
            for pair in curr.children.items():
                c, curr = pair
                answer += c
        return answer

class ProgramClass(App, Trie):
    '''
    Initializes needed variables, such as paths, API key etc.
    Initializes trie (prefix tree) using a list of currencies stored in Google Drive.

    Methods
    -------
    run_program()
        Initializes an object of the App class and runs the main loop.
    '''
    def __init__(self):
        global CURRENCIES_SHORT, EUROPE_CURRENCIES, TARGET_URL, BASE_DIR, API_KEY, trie_object
        # Upload short list of currencies' codes and countries' names from Google Drive to pandas DataSet
        # to add them to the trie
        url_currencies_short = 'https://drive.google.com/file/d/1LFQO13AVf4U0LXOzKEycRYL0gKx3tv1m/'.split('/')[-2]
        url_currencies_short = 'https://drive.google.com/uc?id=' + url_currencies_short
        CURRENCIES_SHORT = pd.read_csv(url_currencies_short)

        # The same, but uploading europe currencies only to check in CurrencyConverter.double_conversion method
        url_europe_currencies = \
            'https://drive.google.com/file/d/1JRSbtOFZ54PPCo55qwA4FfPKjw31NRY5/view?usp=share_link'.split('/')[-2]
        url_europe_currencies = 'https://drive.google.com/uc?id=' + url_europe_currencies
        EUROPE_CURRENCIES = pd.read_csv(url_europe_currencies)

        # API url and absolute address of this module
        TARGET_URL = 'https://www.x-rates.com/calculator/'
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        API_KEY = 'YkvsDr8AFiIpgxr5tLJPPnDQskeez3xU3JJNLgyG'

        # Initializing object of the Trie class to add needed words (names of the countries and currencies' codes)
        # from pandas DataSet CURRENCIES_SHORT
        trie_object = Trie()
        for country in CURRENCIES_SHORT['Country']:
            trie_object.add_word(country.lower())
        for code in CURRENCIES_SHORT['AlphabeticCode']:
            trie_object.add_word(code)
        for country, code in zip(CURRENCIES_SHORT['Country'], CURRENCIES_SHORT['AlphabeticCode']):
            trie_object.currencies_dict[country.lower()] = code

        # Initializing colorama library with needed setting
        # of auto reset of changed colors to avoid mispainting in a terminal
        colorama.init(autoreset=True)

    def run_program(self):
        '''Method with the main loop of the program'''

        # Initializing an object of the App class to work with in further loop
        x = App()
        try:
            # Loop for the main part of the program
            while True:
                x.menu()
                input_num = x.input_choice()
                if input_num == '1':
                    x.app_exchange()
                elif input_num == '2':
                    x.app_double_conversion()
                elif input_num == '3':
                    x.app_show_saved_currencies()
                elif input_num == '4':
                    x.update_rates()
                elif input_num == '5':
                    x.app_create_pairs()
                elif input_num == '6':
                    x.app_delete_pairs()
                elif input_num == '7':
                    x.app_delete_all()
                elif input_num == 'x':
                    x.switch_rate_source()
                else:
                    raise KeyboardInterrupt
                input('\nContinue?\n(Press return)\n')
        except ExchangeError as e:
            print(colorama.Fore.RESET)
            print(e.__str__() + '\nExiting...')
            time.sleep(2)
            exit(0)
        except KeyboardInterrupt:
            print('\nThank you for using the application. Goodbye!')
            time.sleep(2)
            exit(0)
        except urllib.error.HTTPError:
            print('\nCannot read needed datasets. Try to restart the program.\nExiting...')
            time.sleep(2)
            exit(0)
        except:
            print(colorama.Fore.RESET)
            print('\nUnhandled exception occurred. Exiting...')
            time.sleep(2)
            exit(0)


if __name__ == '__main__':
    # Initialize needed variables and run the program
    program = ProgramClass()
    program.run_program()
