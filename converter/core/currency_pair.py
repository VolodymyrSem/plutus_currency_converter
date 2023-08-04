from dataclasses import dataclass

from converter.core.trie import prepare_and_get_word_searcher
from converter.db.db import DBHandler
from converter.handlers.API import APIHandler


@dataclass
class CurrencyPair(DBHandler, APIHandler):
    from_currency: str
    to_currency: str
    amount: float = 1
    card_type: str = None

    def __post_init__(self):
        self.__result: float = None
        self.__word_searcher = prepare_and_get_word_searcher()
        self.__set_from_and_to_currency()
        super().__init__()

    @property
    def result(self) -> float:
        return self.__result

    @result.setter
    def result(self, result: float):
        self.__result = result

    def set_result_from_api(self):
        rate = self.get_rate_from_API(
            self.from_currency,
            self.to_currency
        )
        amount = self.amount

        result = rate * amount
        self.__result = round(result, 5)

    def set_result_from_db(self):
        currencies_to_insert = (
            self.from_currency,
            self.to_currency
        )
        rate = self.get_rate_from_db(currencies_to_insert)
        result = rate * self.amount
        self.__result = round(result, 5)

    def __set_from_and_to_currency(self):
        self.from_currency = self.__word_searcher.get_code(self.from_currency)
        self.to_currency = self.__word_searcher.get_code(self.to_currency)

    def currencies_filled_out(self):
        if not self.from_currency or not self.to_currency:
            return False
        return True

    def get_pair_as_tuple(self):
        return (
            self.from_currency,
            self.to_currency,
            self.amount
        )