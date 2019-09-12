import sqlite3
import numpy as np
from utility import get_setting


class ScatsDB(object):
    """ Stores and retrieves the VicRoads data from the local database """
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
        """ Automatically handles closing the database connection """
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


    def commit(self):
        """ Public method to manually commit changes if needed """
        self.connection.commit()


    def insert_new_scats(self, scats_number, internal_location, location_name, latitude, longitude):
        """ Inserts a brand new scats site/location into the database

        Parameters:
            scats_number (int): the scats site identifier
            internal_location (int): the VicRoads internal id for the location
            location_name (int): the name of the location
            latitude (float): geographic coordinate specifying the north–south position
            longitude (float): geographic coordinate specifying the east–west position
        """
        self.cursor.execute("SELECT scats_number, internal_location FROM scats "
                            "WHERE scats_number = ? AND internal_location = ?", (scats_number, internal_location))

        data = self.cursor.fetchone()

        # This is just a check to make sure the location isn't already in the database
        if data is None:
            self.connection.execute("INSERT INTO scats ("
                                    "scats_number, internal_location, location_name, latitude, longitude) "
                                    "VALUES (?, ?, ?, ?, ?)",
                                    (scats_number, internal_location, location_name, latitude, longitude))


    def insert_scats_data(self, scats_number, internal_location, date, volume):
        """ Inserts the volume data into the database

        Parameters:
            scats_number (int): the scats site identifier
            internal_location (int): the VicRoads internal id for the location
            date (String): the date/time when the specific volume occurred
            volume (int): the volume of traffic for the location
        """
        self.cursor.execute("SELECT scats_number, internal_location, date FROM scats_data "
                            "WHERE scats_number = ? AND internal_location = ? AND date = ?",
                            (scats_number, internal_location, date))

        data = self.cursor.fetchone()
        if data is None:
            self.connection.execute("INSERT INTO scats_data (scats_number, internal_location, date, volume) "
                                    "VALUES (?, ?, ?, ?)", (scats_number, internal_location, date, volume))


    def get_scats_volume(self, scats_number, internal_location):
        """ Gets the volume for a location over the entire time period

        Parameters:
            scats_number (int): the scats site identifier
            internal_location (int): the VicRoads internal id for the location
        """
        self.cursor.execute("SELECT volume FROM scats_data "
                            "WHERE scats_number = ? AND internal_location = ?",
                            (scats_number, internal_location))

        return np.array([item[0] for item in self.cursor.fetchall()])


    def get_all_scats_numbers(self):
        """ Retrieves all the scats numbers """
        self.cursor.execute("SELECT DISTINCT scats_number FROM scats")
        return [item[0] for item in self.cursor.fetchall()]


    def get_location_name(self, scats_number, internal_location):
        """ Gets the name of the location given it's VicRoads internal identifier

        Parameters:
            scats_number (int): the scats site identifier
            internal_location (int): the VicRoads internal id for the location

        Returns:
            String: the name of the location
        """
        self.cursor.execute("SELECT location_name FROM scats WHERE scats_number = ? AND internal_location = ?",
                            (scats_number, internal_location))

        return self.cursor.fetchone()[0]


    def get_location_id(self, location_name):
        """ Gets the VicRoads id of the location given it's name

        Parameters:
            location_name (String): the name of the location

        Returns:
            int: the VicRoads internal id for the location
        """
        self.cursor.execute("SELECT internal_location FROM scats WHERE location_name = ? ",
                            (location_name,))

        return self.cursor.fetchone()[0]


    def get_scats_approaches(self, scats_number):
        """ Gets all the locations a vehicle can approach from given a scats site

        Parameters:
            scats_number (int): the scats site identifier

        Returns:
            array: a list of all the location ids for a scats site
        """
        self.cursor.execute("SELECT internal_location FROM scats WHERE scats_number = ?",
                            (scats_number,))
        return [item[0] for item in self.cursor.fetchall()]


    def get_positional_data(self, scats_number, internal_location):
        """ Gets the longitude and latitude values for a location

        Parameters:
            scats_number (int): the scats site identifier
            internal_location (int): the VicRoads internal id for the location

        Returns:
            float: geographic coordinate specifying the north–south position - latitude
            float: geographic coordinate specifying the east–west position - longitude
        """
        self.cursor.execute("SELECT latitude, longitude FROM scats WHERE scats_number = ? AND internal_location = ?",
                            (scats_number, internal_location))
        return self.cursor.fetchone()[0], self.cursor.fetchone()[1]



