import os
import sqlite3 as sql

from converter.core.currency_pair import CurrencyPair
from converter.core.exceptions import *


class CurrencyConverter:
    """
    Get user's request and compute results.

    Methods
    -------
    exchange
        Returns rate for requested pair of currencies, source of the rate depends on state of the switch at that moment.
    """

    def __init__(self):
        self.rates_are_from_db = False
        self.currency_pair = None

    def exchange(self, currency_pair: CurrencyPair = None) -> CurrencyPair:
        """
        Sets rate of a CurrencyPair object from api or db.
        """

        if currency_pair is None:
            currency_pair = self.currency_pair

        if self.rates_are_from_db:
            currency_pair.set_result_from_db()
        else:
            currency_pair.set_result_from_api()
        return currency_pair

    def switch_rate_source(self):
        self.rates_are_from_db = not self.rates_are_from_db
