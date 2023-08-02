from .currency_converter import CurrencyConverter

from converter.core.trie import EUROPE_CURRENCIES


class CurrencyConverterDoubleConversion(CurrencyConverter):
    def __init__(self):
        super().__init__()

    def double_conversion(self) -> float:
        """
        Returns amount of an owned currency needed to pay for amount of a target currency.
        Result depends on a card system, which may have a consequence of double/triple conversion.
        Uses CurrencyConverter.exchange method as a base method for exchanging currencies.
        """

        if self.__is_card_type_MC() and not self.__is_target_currency_european():
            result = self.__buy_non_european_with_european()

        elif self.__is_card_type_MC():
            result = self.__buy_european_with_european()

        elif not self.__is_card_type_MC() and self.__is_target_currency_european():
            result = self.__buy_european_with_non_european()

        elif not self.__is_card_type_MC():
            result = self.__buy_non_european_with_non_european()

        self.currency_pair.result = result

    def __is_card_type_MC(self):
        return self.currency_pair.card_type == 'MC'

    def __is_target_currency_european(self):
        return self.currency_pair.to_currency in EUROPE_CURRENCIES['AlphabeticCode'].unique()

    def __buy_non_european_with_european(self):
        if self.__is_currency_EUR(is_currency_target=False):
            dc_from_EUR = self.currency_pair.amount
        else:
            dc_from_EUR = self.__divide_and_add_fee(
                self.currency_pair.amount,
                self.__exchange(from_currency='EUR')
            )
        return self.__divide_and_add_fee(
            dc_from_EUR,
            self.__exchange(to_currency='EUR')
        )

    def __buy_european_with_european(self):
        rate = self.__exchange()
        return self.__divide_and_add_fee(
            self.currency_pair.amount,
            rate
        )

    def __buy_european_with_non_european(self):
        if not self.__is_currency_EUR(is_currency_target=True):
            dc_from_EUR = self.__divide_and_add_fee(
                self.currency_pair.amount,
                self.__exchange(from_currency='EUR')
            )
        else:
            dc_from_EUR = self.currency_pair.amount

        dc_from_USD = self.__divide_and_add_fee(
            dc_from_EUR,
            self.__exchange(from_currency='USD', to_currency='EUR')
        )

        if not self.__is_currency_USD(is_currency_target=False):
            result = self.__divide_and_add_fee(
                dc_from_USD,
                self.__exchange(to_currency='USD')
            )
        else:
            result = dc_from_USD
        return result

    def __is_currency_EUR(self, *, is_currency_target: bool):
        currency = self.__get_currency(is_currency_target)
        return currency == 'EUR'

    def __buy_non_european_with_non_european(self):
        if not self.__is_currency_USD(is_currency_target=True):
            dc_from_USD = self.__divide_and_add_fee(
                self.currency_pair.amount,
                self.__exchange(from_currency='USD')
            )
        else:
            dc_from_USD = self.currency_pair.amount

        if not self.__is_currency_USD(is_currency_target=False):
            result = self.__divide_and_add_fee(
                dc_from_USD,
                self.__exchange(to_currency='USD')
            )
        else:
            result = dc_from_USD

        return result

    def __is_currency_USD(self, *, is_currency_target: bool):
        currency = self.__get_currency(is_currency_target)
        return currency == 'USD'

    def __get_currency(self, is_currency_target: bool):
        return (
            self.currency_pair.to_currency if
            is_currency_target else
            self.currency_pair.from_currency
        )

    def __divide_and_add_fee(self, divisor, dividend):
        fee = 1.03 if self.currency_pair.card_type == 'VISA' else 1.02
        return (divisor / dividend) * fee

    def __exchange(self, *, from_currency: str = '', to_currency: str = ''):
        if from_currency:
            original_from = self.currency_pair.from_currency
            self.currency_pair.from_currency = from_currency
        if to_currency:
            original_to = self.currency_pair.to_currency
            self.currency_pair.to_currency = to_currency
        original_amount = self.currency_pair.amount
        self.currency_pair.amount = 1

        self.exchange()
        result = self.currency_pair.result

        if from_currency:
            self.currency_pair.from_currency = original_from
        if to_currency:
            self.currency_pair.to_currency = original_to
        self.currency_pair.amount = original_amount

        return result
