import unittest

from converter.core.currency_pair import CurrencyPair


class TestCurrencyPair(unittest.TestCase):
    def setUp(self) -> None:
        self.currency_pair = CurrencyPair('usa', 'cze', 1, 'MC')

    def test_setting_up_valid_currency_names(self):
        '''
        Test that post init works good for setting up codes of currencies
        '''

        self.assertEqual(self.currency_pair.from_currency, 'USD')
        self.assertEqual(self.currency_pair.to_currency, 'CZK')
        self.assertEqual(self.currency_pair.amount, 1)
        self.assertEqual(self.currency_pair.card_type, 'MC')

    def test_setting_up_invalid_currency_names(self):
        '''
        Test that post init replace invalid currency name with empty string
        '''

        currency_pair = CurrencyPair('EFWE', 'XCSDF', 15, 'MC')
        self.assertEqual(currency_pair.from_currency, '')
        self.assertEqual(currency_pair.to_currency, '')

    def test_checking_emptiness_of_currency_name(self):
        '''
        Test that method currencies_filled_out returns correct value
        '''

        currency_pair = CurrencyPair('EFWE', 'USD', 15, 'MC')
        self.assertFalse(currency_pair.currencies_filled_out())

        self.assertTrue(self.currency_pair.currencies_filled_out())

    def test_result_from_api(self):
        '''
        Test that method set_result_from_api sets a result of valid type
        '''

        self.currency_pair.set_result_from_api()
        self.assertIsInstance(self.currency_pair.result, float)

    def test_result_from_db(self):
        '''
        Test that method set_result_from_db sets a result of valid type
        '''

        self.currency_pair.set_result_from_db()
        self.assertIsInstance(self.currency_pair.result, float)
