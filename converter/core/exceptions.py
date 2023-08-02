
class ExchangeError(Exception):
    '''Base exception for the program'''

    def __init__(self, message='', *args):
        if not message:
            message = self.get_default_message()
        return super().__init__(message, *args)

    def get_default_message(self):
        return None


class ServerError(ExchangeError):
    '''Bad response from the server'''

    def __init__(self, message='', *args):
        super().__init__(message)

    def get_default_message(self):
        return 'Bad response of the server. Please, try to restart the program.'


class DatabaseException(ExchangeError):
    '''Base exception for database errors'''

    pass


class DatabaseNotExistError(DatabaseException):
    '''DB file is not in directory'''

    def __init__(self, message='', *args):
        super().__init__(message)

    def get_default_message(self):
        return ('The database is empty or doesn\'t exist.\n'
               'Restart the program and choose "Refresh your database".')

class EmptySavedPairsTableException(DatabaseNotExistError):
    '''Saved pairs table is empty'''

    def __init__(self, message='', *args):
        super().__init__(message)

    def get_default_message(self):
        return ('Can\'t find any saved pairs of currencies.\n'
               'Create them first, please.')


class NoSuchPairException(DatabaseException):
    '''Can't find provided pair in saved pairs table'''

    pass
