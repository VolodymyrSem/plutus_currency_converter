CREATE_TABLE_PREPARED_CURRENCIES = '''
    CREATE TABLE IF NOT EXISTS prepared_currencies (
    id INTEGER PRIMARY KEY,
    from_currency STRING,
    to_currency STRING,
    rate REAL,
    UNIQUE(from_currency, to_currency)
    )
'''

CREATE_TABLE_SAVED_CURRENCIES = '''
    CREATE TABLE IF NOT EXISTS saved_currencies (
    id INTEGER PRIMARY KEY,
    from_currency STRING,
    to_currency STRING,
    amount INTEGER,
    UNIQUE(from_currency, to_currency)
    )
'''

GET_RATE = '''
    SELECT rate FROM prepared_currencies 
    WHERE from_currency = (?) 
    AND to_currency = (?)
'''

GET_LAST_PAIR_FROM_PREPARED_CURRENCIES = '''
    SELECT max(id) from prepared_currencies
'''

INSERT_PAIR_IN_PREPARED_CURRENCIES = '''
    INSERT INTO 
    prepared_currencies (from_currency, to_currency, rate)
    VALUES (?, ?, ?)
'''

INSERT_NEW_PAIR_IN_SAVED_CURRENCIES = '''
    INSERT OR IGNORE INTO 
    saved_currencies (from_currency, to_currency, amount)
    VALUES (?, ?, ?)
'''

GET_SAVED_CURRENCIES = '''
    SELECT from_currency, to_currency, amount
    FROM saved_currencies
'''

GET_PAIR_FROM_SAVED_CURRENCIES = '''
    SELECT *
    FROM saved_currencies
    WHERE from_currency = (?)
    AND to_currency = (?)
'''

DELETE_PAIR_FROM_SAVED_CURRENCIES = '''
    DELETE FROM saved_currencies 
    WHERE from_currency = ?
    AND to_currency = ?
'''

DELETE_ALL_FROM_SAVED_CURRENCIES = '''
    DELETE FROM saved_currencies
'''

DELETE_ALL_FROM_PREPARED_CURRENCIES = '''
    DELETE FROM prepared_currencies
'''


