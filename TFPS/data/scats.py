from datetime import datetime

import os.path

import numpy as np
import pandas as pd
import overpass as op
import unicodecsv
import xlrd

from datetime import datetime, timedelta

import utility


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
    MAPPING_DATA = "data/MappingData.xls"

    CONVENTIONS = {"RD": "Road",
                   "ST": "Street",
                   "HWY": "Highway",
                   "GV": "Grove",
                   "EASTERN": "Eastern Freeway"}

    RELATIVE_LAT, RELATIVE_LONG = -37.9161, 144.9596
    DIRECTIONS_SINE = np.empty((8,))
    DIRECTIONS_COSINE = np.empty((8,))
    SIN_TIMES = np.empty((96,))
    COS_TIMES = np.empty((96,))

    MAX_TRAFFIC = 1000

    DEFAULT_SPEED_LIMIT = 60
    USE_SPEED_LIMITS_FROM_OSM = False

    def __init__(self):
        # Load all the SCATS data
        if not os.path.exists(self.CSV_FILE):
            convert_to_csv(self.DATA_SOURCE, self.CSV_FILE)
        dataset = pd.read_csv(self.CSV_FILE, encoding="latin-1", sep=",", header=None)
        self.data = pd.DataFrame(dataset)
        self.data[9] = format_date(self.data[9])

        for i in range(8):
            self.DIRECTIONS_SINE[i] = 0.5 * np.sin(2 * np.pi * i / 8) + 0.5
            self.DIRECTIONS_COSINE[i] = 0.5 * np.cos(2 * np.pi * i / 8) + 0.5
        for i in range(96):
            self.SIN_TIMES[i] = 0.5 * np.sin(2 * np.pi * i / 96) + 0.5
            self.COS_TIMES[i] = 0.5 * np.cos(2 * np.pi * i / 96) + 0.5

        self.roads = pd.DataFrame(columns=["0", "1", "2", "3", "4"])
        if not self.USE_SPEED_LIMITS_FROM_OSM and os.path.exists(self.MAPPING_DATA):
            roads_data = pd.read_excel(self.MAPPING_DATA, sheet_name='NodeConnections', skiprows=1)
            self.roads = pd.DataFrame(roads_data)

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

        return raw_data.iloc[0][3], raw_data.iloc[0][4]

    def get_relational_positional_data(self, scats_number, location):

        absolute_lat, absolute_long = self.get_positional_data(scats_number, location)

        return absolute_lat - self.RELATIVE_LAT, absolute_long - self.RELATIVE_LONG

    def get_speed_limit(self, begin_scats_number, begin_location, end_scats_number, end_location):
        """ Gets the speed limit for a section of road

        Parameters:
            begin_scats_number (int): the scats site identifier for the start of the road
            begin_location (int): the VicRoads internal id/direction for the start of the road
            end_scats_number (int): the scats site identifier for the end of the road
            end_location (int): the VicRoads internal id/direction for the end of the road

        Returns:
            int: the speed limit of the road (in km/h)
        """
        if self.USE_SPEED_LIMITS_FROM_OSM:
            speed_limit = self.get_speed_limit_from_osm(begin_scats_number, begin_location,
                                                        end_scats_number, end_location)
        else:
            speed_limit = self.get_speed_limit_from_file(begin_scats_number, begin_location,
                                                         end_scats_number, end_location)

        return speed_limit

    def get_speed_limit_from_file(self, begin_scats_number, begin_location, end_scats_number, end_location):
        """ Gets the speed limit for a section of road from the Mapping Data file

        Parameters:
            begin_scats_number (int): the scats site identifier for the start of the road
            begin_location (int): the VicRoads internal id/direction for the start of the road
            end_scats_number (int): the scats site identifier for the end of the road
            end_location (int): the VicRoads internal id/direction for the end of the road

        Returns:
            int: the speed limit of the road (in km/h)
        """
        speed_limit = self.DEFAULT_SPEED_LIMIT

        start_road = "{0}-{1}".format(begin_scats_number, begin_location)
        end_road = "{0}-{1}".format(end_scats_number, end_location)

        try:
            raw_data = self.roads.loc[(self.roads[1] == start_road) & (self.roads[2] == end_road)]
            speed_limit = raw_data.iloc[0][3]
        except KeyError:
            pass

        return speed_limit

    def get_speed_limit_from_osm(self, begin_scats_number, begin_location, end_scats_number, end_location):
        """ Gets the speed limit for a section of road from OpenStreetMaps

        Parameters:
            begin_scats_number (int): the scats site identifier for the start of the road
            begin_location (int): the VicRoads internal id/direction for the start of the road
            end_scats_number (int): the scats site identifier for the end of the road
            end_location (int): the VicRoads internal id/direction for the end of the road

        Returns:
            int: the speed limit of the road (in km/h)
        """
        speed_limit = self.DEFAULT_SPEED_LIMIT

        api = op.API(endpoint="https://lz4.overpass-api.de/api/interpreter", timeout=60)

        s_latitude, s_longitude = self.get_positional_data(begin_scats_number, begin_location)
        e_latitude, e_longitude = self.get_positional_data(end_scats_number, end_location)

        location = (self.get_location_name(begin_scats_number, begin_location)).split("_")

        road_name = location[0].title()
        road_type = self.CONVENTIONS[location[1].split(" ")[0]]
        name = "{0} {1}".format(road_name, road_type)

        way = 'way["name"~"{0}"]({1},{2},{3},{4});(._;>;)'
        if s_latitude < e_latitude:
            if s_longitude < e_longitude:
                way = way.format(road_name, s_latitude, s_longitude, e_latitude, e_longitude)
            else:
                way = way.format(road_name, s_latitude, e_longitude, e_latitude, s_longitude)
        else:
            if s_longitude < e_longitude:
                way = way.format(road_name, e_latitude, s_longitude, s_latitude, e_longitude)
            else:
                way = way.format(road_name, e_latitude, e_longitude, s_latitude, s_longitude)

        data = api.get(way, verbosity='geom')
        for feature in data["features"]:
            properties = feature["properties"]

            name_fields = ["name", "alt-name"]
            for name_field in name_fields:
                if name_field in properties.keys():
                    if properties[name_field] == name:
                        if "maxspeed" in properties.keys():
                            speed_limit = int(properties["maxspeed"])

        return speed_limit

    def get_training_data(self):
        train_data = np.zeros((len(self.data) * 96, 7))
        count = 0
        rows = self.data.to_numpy()
        for i in range(len(rows)):
            row = rows[i]
            lat, long = utility.convert_absolute_coordinates_to_relative(row[3], row[4])
            direction = int(row[7])
            volume = row[10:106]
            valid_junction = False
            if 0 < direction < 9:
                valid_junction = True
            for n in range(96):
                train_data[count][0] = lat
                train_data[count][1] = long
                if valid_junction:
                    train_data[count][2] = self.DIRECTIONS_SINE[direction - 1]
                    train_data[count][3] = self.DIRECTIONS_COSINE[direction - 1]
                train_data[count][4] = self.SIN_TIMES[n]
                train_data[count][5] = self.COS_TIMES[n]
                train_data[count][6] = volume[n] / self.MAX_TRAFFIC
                count += 1
        np.random.shuffle(train_data)
        return train_data[0:, 0:6], train_data[0:, 6:]
