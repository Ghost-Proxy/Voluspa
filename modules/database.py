import sqlite3
import os


class Database(object):

    # TODO:
    # Handle closing. (e.g. conn.close())
    # Handle checking if db exists or not for creation

    def __init__(self):
        self.database_name = 'voluspa.db'
        self.database = self.connect()
        self.cursor = self.database.cursor()
        # self.create_tables()

    def connect(self):
        return sqlite3.connect(self.database_name)

    def create_tables(self):
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



