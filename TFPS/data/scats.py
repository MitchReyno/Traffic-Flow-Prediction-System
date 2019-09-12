import sqlite3
import numpy as np
from utility import get_setting


class ScatsDB(object):
    def __init__(self):
        create_scats_table = "CREATE TABLE IF NOT EXISTS scats (scats_number INTEGER NOT NULL, " \
                             "internal_location INTEGER NOT NULL, location_name TEXT NOT NULL, latitude TEXT NOT NULL, " \
                             "longitude TEXT NOT NULL, PRIMARY KEY (scats_number, internal_location));"

        create_data_table = "CREATE TABLE IF NOT EXISTS scats_data (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                            "scats_number INTEGER NOT NULL, internal_location INTEGER NOT NULL, date TEXT NOT NULL, " \
                            "volume INTEGER NOT NULL, FOREIGN KEY(scats_number, internal_location) " \
                            "REFERENCES scats(scats_number, internal_location));"

        self.connection = sqlite3.connect("data/" + get_setting("database"))
        self.cursor = self.connection.cursor()

        self.connection.execute(create_data_table)
        self.connection.execute(create_scats_table)

        self.connection.commit()


    def __enter__(self):
        return self


    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


    def commit(self):
        self.connection.commit()


    def insert_new_scats(self, scats_number, internal_location, location_name, latitude, longitude):
        self.cursor.execute("SELECT scats_number, internal_location FROM scats "
                            "WHERE scats_number = ? AND internal_location = ?", (scats_number, internal_location))

        data = self.cursor.fetchone()
        if data is None:
            self.connection.execute("INSERT INTO scats ("
                                    "scats_number, internal_location, location_name, latitude, longitude) "
                                    "VALUES (?, ?, ?, ?, ?)",
                                    (scats_number, internal_location, location_name, latitude, longitude))


    def insert_scats_data(self, scats_number, internal_location, date, volume):
        self.cursor.execute("SELECT scats_number, internal_location, date FROM scats_data "
                            "WHERE scats_number = ? AND internal_location = ? AND date = ?",
                            (scats_number, internal_location, date))

        data = self.cursor.fetchone()
        if data is None:
            self.connection.execute("INSERT INTO scats_data (scats_number, internal_location, date, volume) "
                                    "VALUES (?, ?, ?, ?)", (scats_number, internal_location, date, volume))


    def get_scats_volume(self, scats_number, internal_location):
        self.cursor.execute("SELECT volume FROM scats_data "
                            "WHERE scats_number = ? AND internal_location = ?",
                            (scats_number, internal_location))

        return np.array([item[0] for item in self.cursor.fetchall()])


    def get_all_scats_numbers(self):
        self.cursor.execute("SELECT DISTINCT scats_number FROM scats")
        return [item[0] for item in self.cursor.fetchall()]


    def get_location_name(self, scats_number, internal_location):
        self.cursor.execute("SELECT location_name FROM scats WHERE scats_number = ? AND internal_location = ?",
                            (scats_number, internal_location))

        return self.cursor.fetchone()[0]


    def get_location_id(self, location_name):
        self.cursor.execute("SELECT internal_location FROM scats WHERE location_name = ? ",
                            (location_name,))

        return self.cursor.fetchone()[0]


    def get_scats_approaches(self, scats_number):
        self.cursor.execute("SELECT internal_location FROM scats WHERE scats_number = ?",
                            (scats_number,))
        return [item[0] for item in self.cursor.fetchall()]


    def get_positional_data(self, scats_number, internal_location):
        self.cursor.execute("SELECT latitude, longitude FROM scats WHERE scats_number = ? AND internal_location = ?",
                            (scats_number, internal_location))
        return self.cursor.fetchone()[0], self.cursor.fetchone()[1]



