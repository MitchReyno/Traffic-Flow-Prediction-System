"""
Processing the data
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from time import gmtime, strftime
from data.scats import ScatsDB


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
                s.insert_new_scats(current_scats, current_junction, row[4], row[5])
            else:
                if row[8] != current_junction:
                    current_junction = row[8]
                    s.insert_new_scats(current_scats, current_junction, row[4], row[5])

            for i in range(96):
                current_time = row[10] + " " + format_time(i)
                value = row[11 + i]
                s.insert_scats_data(current_scats, current_junction, current_time, value)


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
        scaler: StandardScaler.
    """
    with ScatsDB() as s:
        volume = s.get_scats_volume(scats_number, junction)

        # scaler = StandardScaler().fit(volume.values)
        scaler = MinMaxScaler(feature_range=(0, 1)).fit(volume.reshape(-1, 1))
        flow1 = scaler.transform(volume.reshape(-1, 1)).reshape(1, -1)[0]

        train = []
        for i in range(lags, len(flow1)):
            train.append(flow1[i - lags: i + 1])

        train = np.array(train)
        np.random.shuffle(train)

        x_train = train[:, :-1]
        y_train = train[:, -1]

        return x_train, y_train, scaler
