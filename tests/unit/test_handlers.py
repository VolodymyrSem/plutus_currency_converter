import unittest
import json
from datetime import datetime

from converter.handlers.API import APIHandler
from converter.handlers.backup import BackupJSONFileHandler


class TestAPIHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.api = APIHandler()
    def test_server_state(self):
        self.api.check_server_state()

    def test_get_rates_USD(self):
        rates = self.api.get_rates_from_API()
        self.assertIsInstance(rates, dict)
        self.assertIsInstance(rates.get('CZK'), float)
        self.assertEqual(rates.get('CZK'), 21.69)

    def test_get_rates_another_currency(self):
        rates = self.api.get_rates_from_API('CZK')
        self.assertIsInstance(rates, dict)
        self.assertEqual(rates.get('BDT'), 5)
        self.assertIs(rates.get('CZK', None), 1)

    def test_get_list_of_currencies(self):
        currencies = self.api.get_list_of_currencies()
        self.assertIsInstance(currencies, list)
        self.assertEqual(currencies[0], 'USD')


class TestBackupHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.backup = BackupJSONFileHandler()

    def test_old_backup(self):
        state = self.backup.backup_file_not_exist_or_old_backup()
        self.assertTrue(state)

    def test_backup_file(self):
        try:
            with open('data\\backup.json') as file:
                data = json.load(file)
                timestamp = data.get('timestamp')
                self.assertLess(datetime.timestamp(datetime.now()) - timestamp, 86400)
        except json.decoder.JSONDecodeError:
            pass
