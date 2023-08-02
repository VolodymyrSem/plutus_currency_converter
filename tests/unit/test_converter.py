import unittest

from converter.core.currency_converter import CurrencyConverter
from converter.core.currency_pair import CurrencyPair


class TestCurrencyConverter(unittest.TestCase):
    def setUp(self) -> None:
        self.converter = CurrencyConverter()
        self.converter.currency_pair = CurrencyPair('CAD', 'CZK', 50)

    def test_converter_exchange_on_place(self):
        self.converter.exchange()
        self.assertAlmostEqual(self.converter.currency_pair.result, 16.43 * 50, 2)
        self.assertIsInstance(self.converter.currency_pair.result, float)

        self.converter.switch_rate_source()

        self.converter.exchange()
        self.assertIsInstance(self.converter.currency_pair.result, float)

    def test_converter_exchange_explicit(self):
        currency_pair = CurrencyPair('GBP', 'UAH')
        currency_pair = self.converter.exchange(currency_pair)
        self.assertIsInstance(currency_pair.result, float)

    def test_change_rate_source(self):
        self.assertFalse(self.converter.rates_are_from_db)

        self.converter.switch_rate_source()

        self.assertTrue(self.converter.rates_are_from_db)
