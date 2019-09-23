import os
from math import asin
from time import gmtime, strftime

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from data.scats import ScatsDB


def check_data_exists():
    """ Returns True if the db is populated with some data """
    not_empty = False

    with ScatsDB() as s:
        if s.count_data() > 0:
            not_empty = True

    return not_empty


def format_time(index):
    """ Converts an index into a time value

    Parameters:
        index (int): the column index

    Returns:
        String: the time value associated with the column index
    """
    return strftime("%H:%M", gmtime(index * 15 * 60))


def format_date(date):
    """ Converts a date into the desired local format

    Parameters:
        date (String): the date to be converted

    Returns:
        String: the date in the format of 01/01/2019
    """
    return pd.datetime.strftime(date, "%d/%m/%Y")


def read_data(data):
    """ Reads in data from an Excel spreadsheet and stores the information in a database

    Parameters:
        data (String): the path to the file containing the VicRoads dataset
    """
    # skiprows: Used to ignore the header
    # date_parser: Formats the date as the data is being read in, might be the cause of slow loading times?
    # nrows: Can be removed, limits the amount of data being read in
    dataset = pd.read_excel(data, sheet_name='Data', skiprows=1, parse_dates=['Date'], date_parser=format_date,
                            nrows=200)
    df = pd.DataFrame(dataset)

    current_scats = None
    current_junction = None
    with ScatsDB() as s:
        # Loop through each row and add the values to the database
        for row in df.itertuples():
            if row[1] != current_scats:
                current_scats = row[1]
                current_junction = row[8]
                # The 4th and 5th index of the row are the latitude and longitude values
                # The 2nd index is the location name
                s.insert_new_scats(current_scats, current_junction, row[2], row[4], row[5])
            else:
                if row[8] != current_junction:
                    current_junction = row[8]
                    s.insert_new_scats(current_scats, current_junction, row[2], row[4], row[5])

            for i in range(96):
                # The date value is at the 10th index
                current_time = row[10] + " " + format_time(i)
                # The volume starts at the 11th index
                value = row[11 + i]
                s.insert_scats_data(current_scats, current_junction, current_time, value)

    print("Loading complete")


def process_data(scats_number, junction, lags):
    """Process the VicRoads data into a more readable format

    Parameters:
        scats_number (int): then number of the scats site
        junction (int): the VicRoads internal id representing the location
        lags (int): time lag

    Returns:
        array: x_train
        array: y_train
        array: x_test
        array: y_test
        StandardScaler: the scaler used to reshape the training data
    """
    with ScatsDB() as s:
        volume_data = s.get_scats_volume(scats_number, junction)
        print(f"(data.py) VOLUME DATA: {volume_data[:10]}")
        print(f"(data.py) VOLUME DATA SHAPE: {volume_data.shape}")
        # Training using the first 3 weeks.
        volume_training = volume_data[:2016]
        # Testing using the remaining days of the month.
        volume_testing = volume_data[2016:]

        # scaler = StandardScaler().fit(volume.values)
        # Fit training data between feature range (0-1) | Reshape array to be (unknown, 1)
        scaler = MinMaxScaler(feature_range=(0, 1)).fit(volume_training.reshape(-1, 1))
        print(f"(data.py) SCALER: {scaler}")
        print(f"(data.py) SCALER TRAIN VOLUME SHAPE: {volume_training.reshape(-1, 1).shape}")
        flow1 = scaler.transform(volume_training.reshape(-1, 1)).reshape(1, -1)[0]
        print(f"(data.py) FLOW1 ELEMENTS: {flow1[:5]}")
        print(f"(data.py) FLOW1 SHAPE: {flow1.shape}")
        flow2 = scaler.transform(volume_testing.reshape(-1, 1)).reshape(1, -1)[0]
        print(f"(data.py) FLOW2 ELEMENTS: {flow2[:5]}")
        print(f"(data.py) FLOW2 SHAPE: {flow2.shape}")

        print(f"(data.py) LAGS: {lags}")
        print(f"(data.py) APPENDED DATA: {flow1[1000 - lags: 1000 + 1]}")
        train, test = [], []
        for i in range(lags, len(flow1)):
            train.append(flow1[i - lags: i + 1]) # from i - lags to i + 1 -  Appending batches of 12 items?
            print(f"(data.py) APPENDED DATA: i = {i} flow = {flow1[i - lags: i + 1]}")
        for i in range(lags, len(flow2)):
            test.append(flow2[i - lags: i + 1])

        train = np.array(train)
        test = np.array(test)
        np.random.shuffle(train)

        x_train = train[:, :-1]
        y_train = train[:, -1]
        x_test = test[:, :-1]
        y_test = test[:, -1]

        return x_train, y_train, x_test, y_test, scaler


def get_location_id(location_name):
    """ Finds the internal location id given it's name

    Parameters:
        location_name (String): the name of the location

    Returns:
        int: the VicRoads internal location id
    """
    if location_name != "All":
        with ScatsDB() as s:
            location = s.get_location_id(location_name)
    else:
        # This handles the case when the user is training the mode for more than 1 location at once
        location = "all"

    return location


def distance_between_points(o_scats, o_junction, d_scats, d_junction):
    """ Finds the great-circle distance between two points

    Parameters:
        o_scats (int): the origin scats site
        o_junction (int): the origin location
        d_scats (int): the destination scats site
        d_junction (int): the destination

    Returns:
        int: the distance in km between the two points
    """
    # The earth's volumetric mean radius
    earth_radius = 6371

    with ScatsDB() as s:
        o_latitude, o_longitude = s.get_positional_data(o_scats, o_junction)
        d_latitude, d_longitude = s.get_positional_data(d_scats, d_junction)

        # Converts all the values into radians
        o_latitude, o_longitude, d_latitude, d_longitude = \
            map(np.radians, (o_latitude, o_longitude, d_latitude, d_longitude))

        # Gets the difference between latitude and longitude values
        dist_latitude = d_latitude - o_latitude
        dist_longitude = d_longitude - o_longitude

        # Applies the haversine formula
        h = np.sin(dist_latitude / 2) ** 2 + np.cos(o_latitude) * np.cos(d_latitude) * np.sin(
            dist_longitude / 2) ** 2

        return 2 * earth_radius * asin(np.sqrt(h))



