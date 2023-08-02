import os
import json
from datetime import datetime

class BackupJSONFileHandler:
    def get_timestamp_from_backup(self):
        try:
            with open('data\\backup.json') as file:
                data = json.load(file)
                return data.get('timestamp', 0)
        except json.decoder.JSONDecodeError:
            return 0

    def rewrite_backup(self, backup_data: dict):
        backup_data_with_timestamp = self.__add_timestamp_to_backup(backup_data)

        with open('data\\backup.json', 'wt') as file:
            file.flush()
            json.dump(backup_data_with_timestamp, file)

    def __add_timestamp_to_backup(self, backup_data: dict) -> dict:
        backup_data['timestamp'] = datetime.timestamp(datetime.now())
        return backup_data