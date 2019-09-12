"""
Processing the data
"""
import os
from math import asin
from time import gmtime, strftime

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from data.scats import ScatsDB
from utility import get_setting


def check_data_exists():
    return os.path.exists("data/{0}".format(get_setting("database")))


def format_time(index):
    return strftime("%H:%M", gmtime(index * 15 * 60))


def format_date(date):
    return pd.datetime.strftime(date, "%d/%m/%Y")


def read_data(data):
    dataset = pd.read_excel(data, sheet_name='Data', skiprows=1, parse_dates=['Date'], date_parser=format_date,
                            nrows=200)
    df = pd.DataFrame(dataset)

    current_scats = None
    current_junction = None
    with ScatsDB() as s:
        for row in df.itertuples():
            if row[1] != current_scats:
                current_scats = row[1]
                current_junction = row[8]
                s.insert_new_scats(current_scats, current_junction, row[2], row[4], row[5])
            else:
                if row[8] != current_junction:
                    current_junction = row[8]
                    s.insert_new_scats(current_scats, current_junction, row[2], row[4], row[5])

            for i in range(96):
                current_time = row[10] + " " + format_time(i)
                value = row[11 + i]
                s.insert_scats_data(current_scats, current_junction, current_time, value)

    print("Loading complete")


def process_data(scats_number, junction, lags):
    """Process data
    Reshape and split VicRoads data.

    # Arguments
        scats_number: integer, then number of the SCATS site.
        junction: integer, the VicRoads internal number representing the location.
        lags: integer, time lag.
    # Returns
        x_train: ndarray.
        y_train: ndarray.
        x_test: ndarray.
        y_test: ndarray.
        scaler: StandardScaler.
    """
    with ScatsDB() as s:
        volume_data = s.get_scats_volume(scats_number, junction)
        # Training using the first 3 weeks.
        volume_training = volume_data[:2016]
        # Testing using the remaining days of the month.
        volume_testing = volume_data[2016:]

        # scaler = StandardScaler().fit(volume.values)
        scaler = MinMaxScaler(feature_range=(0, 1)).fit(volume_training.reshape(-1, 1))
        flow1 = scaler.transform(volume_training.reshape(-1, 1)).reshape(1, -1)[0]
        flow2 = scaler.transform(volume_testing.reshape(-1, 1)).reshape(1, -1)[0]

        train, test = [], []
        for i in range(lags, len(flow1)):
            train.append(flow1[i - lags: i + 1])
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
    if location_name != "All":
        with ScatsDB() as s:
            location = s.get_location_id(location_name)
    else:
        location = "all"

    return location


def distance_between_points(o_scats, o_junction, d_scats, d_junction):
    earth_radius = 6371

    with ScatsDB() as s:
        o_latitude, o_longitude = s.get_positional_data(o_scats, o_junction)
        d_latitude, d_longitude = s.get_positional_data(d_scats, d_junction)

        o_latitude, o_longitude, d_latitude, d_longitude = \
            map(np.radians, (o_latitude, o_longitude, d_latitude, d_longitude))

        dist_latitude = d_latitude - o_latitude
        dist_longitude = d_longitude - o_longitude

        h = np.sin(dist_latitude / 2) ** 2 + np.cos(o_latitude) * np.cos(d_latitude) * np.sin(
            dist_longitude / 2) ** 2

        return 2 * earth_radius * asin(np.sqrt(h))



