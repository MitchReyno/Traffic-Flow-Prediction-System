from datetime import datetime

import os.path

import numpy as np
import pandas as pd
import unicodecsv
import xlrd


def check_data_exists():
    """ Returns True if the scats data csv file exists """
    return os.path.exists("Scats Data.csv")


def format_date(column):
    """ Converts a column of dates into the d/m/Y format with caching for performance.

    Parameters:
        column (DataFrame): the column of dates

    Returns:
        DataFrame: the converted dates column
    """
    dates = {date: pd.datetime.strftime(datetime(*xlrd.xldate_as_tuple(
        date, 0)), "%d/%m/%Y") for date in column}
    return column.map(dates)


def convert_to_csv(input_name, output_name):
    """ Converts an xls spreadsheet into a csv file

    Parameters:
        input_name (String): the file name for the data to be loaded
        output_name (String): the file name for the output csv
    """
    spreadsheet = xlrd.open_workbook(input_name).sheet_by_index(1)

    file = open(output_name, "wb")
    data = unicodecsv.writer(file, encoding="latin-1")

    for n in range(2, spreadsheet.nrows):
        data.writerow(spreadsheet.row_values(n))

    file.close()


class ScatsData(object):
    """ Stores and retrieves the VicRoads data """
    DATA_SOURCE = "data/Scats Data October 2006.xls"
    CSV_FILE = "data/Scats Data.csv"

    def __init__(self):
        if not os.path.exists(self.CSV_FILE):
            convert_to_csv(self.DATA_SOURCE, self.CSV_FILE)

        dataset = pd.read_csv(self.CSV_FILE, encoding="latin-1", sep=",", header=None)
        self.data = pd.DataFrame(dataset)
        self.data[9] = format_date(self.data[9])

    def __enter__(self):
        return self

    def get_scats_volume(self, scats_number, location):
        """ Gets the volume for a location over the entire time period

        Parameters:
            scats_number (int): the scats site identifier
            location (int): the VicRoads internal id/direction for the location
        """
        raw_data = self.data.loc[(self.data[0] == scats_number) & (self.data[7] == location)]

        volume_data = []
        for i in raw_data.index:
            for n in range(10, 106):
                volume_data.append(int(raw_data[n].loc[i]))

        return np.array(volume_data)

    def get_all_scats_numbers(self):
        """ Retrieves all the scats numbers """
        return self.data[0].unique()

    def count(self):
        """ Counts the number of rows in the database """
        return len(self.data.index)

    def get_location_name(self, scats_number, location):
        """ Gets the name of the location given it's VicRoads internal identifier

        Parameters:
            scats_number (int): the scats site identifier
            location (int): the VicRoads internal id/direction for the location

        Returns:
            String: the name of the location
        """
        raw_data = self.data.loc[(self.data[0] == scats_number) & (self.data[7] == location)]

        return raw_data.iloc[0][1]

    def get_location_id(self, location_name):
        """ Gets the VicRoads id of the location given it's name

        Parameters:
            location_name (String): the name of the location

        Returns:
            int: the VicRoads internal id/direction for the location
        """
        raw_data = self.data.loc[self.data[1] == location_name]

        return raw_data.iloc[0][7]

    def get_scats_approaches(self, scats_number):
        """ Gets all the locations a vehicle can approach from given a scats site

        Parameters:
            scats_number (int): the scats site identifier

        Returns:
            array: a list of all the location ids for a scats site
        """
        raw_data = self.data.loc[self.data[0] == scats_number]

        return [int(location) for location in raw_data[7].unique()]

    def get_positional_data(self, scats_number, location):
        """ Gets the longitude and latitude values for a location

        Parameters:
            scats_number (int): the scats site identifier
            location (int): the VicRoads internal id/direction for the location

        Returns:
            float: geographic coordinate specifying the north–south position - latitude
            float: geographic coordinate specifying the east–west position - longitude
        """
        raw_data = self.data.loc[(self.data[0] == scats_number) & (self.data[7] == location)]

        return raw_data[3].loc[0], raw_data[4].loc[0]
