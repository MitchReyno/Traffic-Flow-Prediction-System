import os
from math import asin
from time import gmtime, strftime

import numpy as np
import pandas as pd
from keras.engine.saving import load_model
from sklearn.preprocessing import MinMaxScaler

from data.scats import ScatsData
from utility import get_setting


SCATS_DATA = ScatsData()


def format_time_to_index(time):
    """ Converts a time value into a index

    Parameters:
        time (String): the time value

    Returns:
        int: an index that represents the time
    """
    time_places = time.split(":")
    hours = int(time_places[0])
    minutes = int(time_places[1])
    total_minutes = hours * 60 + minutes

    return (0, total_minutes / 15)[total_minutes > 0]


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
    volume_data = SCATS_DATA.get_scats_volume(scats_number, junction)
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
        train.append(flow1[i - lags: i + 1])  # from i - lags to i + 1 -  Appending batches of 13 items?
    for i in range(lags, len(flow2)):
        test.append(flow2[i - lags: i + 1])

    train = np.array(train)
    test = np.array(test)
    print(f"(data.py) TRAIN SHAPE: {train.shape}")
    print(f"(data.py) TEST SHAPE: {test.shape}")

    np.random.shuffle(train)    # Shuffle training data

    x_train = train[:, :-1]     # Training data         Remove 1 as we're only interested in lags time steps
    y_train = train[:, -1]      # Training labels       Drop right column so we're left with labels.
    x_test = test[:, :-1]       # Testing data
    y_test = test[:, -1]        # Testing labels

    print(f"(data.py) XTRAIN SHAPE: {x_train.shape}")
    print(f"(data.py) YTRAIN SHAPE: {y_train.shape}")

    return x_train, y_train, x_test, y_test, scaler


def get_distance_between_points(o_scats, o_junction, d_scats, d_junction):
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

    o_latitude, o_longitude = SCATS_DATA.get_positional_data(o_scats, o_junction)
    d_latitude, d_longitude = SCATS_DATA.get_positional_data(d_scats, d_junction)

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


def get_volume(scats, junction, time):
    """ Gets the predicted volume for a scats location at a particular time

    Parameters:
        scats (int): the number of the SCATS site
        junction (int): the VicRoads internal number representing the location
        time (String): the time of day in the format of ##:##

    Returns:
        int: the volume of traffic
    """
    model = None

    model_name = get_setting("model").lower()
    file = "model/{0}/{1}/{2}.h5".format(model_name, scats, junction)

    if os.path.exists(file):
        model = load_model(file)

    lag = get_setting("train")["lag"]
    _, _, x_test, y_test, scaler = process_data(scats, junction, lag)

    if model_name == 'SAEs':
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1]))
    else:
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    predicted = model.predict(x_test)
    predicted = scaler.inverse_transform(predicted.reshape(-1, 1)).reshape(1, -1)[0]
    volume_data = predicted[:96]

    return volume_data[int(format_time_to_index(time))]


def get_time_between_points(o_scats, o_junction, d_scats, d_junction, time):
    """ Finds the time it would take to travel between two points

    Parameters:
        o_scats (int): the origin scats site
        o_junction (int): the origin location
        d_scats (int): the destination scats site
        d_junction (int): the destination
        time (String): the time of day ##:##

    Returns:
        float: the time in minutes to travel from one location to another
    """
    volume = get_volume(o_scats, o_junction, time)
    distance = get_distance_between_points(o_scats, o_junction, d_scats, d_junction)
    speed = SCATS_DATA.get_speed_limit(o_scats, o_junction, d_scats, d_junction)

    return distance  / speed