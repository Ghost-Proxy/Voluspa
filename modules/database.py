"""Database Module"""

import sqlite3


class Database(object):
    """Databse class"""

    # TODO:
    # Handle closing. (e.g. conn.close())
    # Handle checking if db exists or not for creation

    def __init__(self):
        self.database_name = 'voluspa.db'
        self.database = self.connect()
        self.cursor = self.database.cursor()
        # self.create_tables()

    def connect(self):
        """Connect to the DB"""
        return sqlite3.connect(self.database_name)

    def create_tables(self):
        """Create required tables"""
        # Create days(id, date, availability_id)
        self.cursor.execute('''
            CREATE TABLE days(
                id INTEGER PRIMARY KEY ASC NOT NULL,
                date TEXT,
                activity_id INTEGER
            );
        ''')

        # Create activities(id, day_id)
        # Create users(id, name, availability_id)
        # Create availabilities(id,
        # Day -> Users -> Times
