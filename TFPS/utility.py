import datetime
import json
import numpy as np
from PyQt5 import QtCore
from datetime import date

RELATIVE_LAT, RELATIVE_LONG = -37.9161, 144.9596
DIRECTIONS_SINE = np.empty((8,))
DIRECTIONS_COSINE = np.empty((8,))
SIN_TIMES = np.empty((96,))
COS_TIMES = np.empty((96,))
SIN_DAYS = {}
COS_DAYS = {}
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
TIME_INTERVALS = {}
for i in range(8):
    DIRECTIONS_SINE[i] = 0.5 * np.sin(2 * np.pi * i / 8) + 0.5
    DIRECTIONS_COSINE[i] = 0.5 * np.cos(2 * np.pi * i / 8) + 0.5
for i in range(96):
    SIN_TIMES[i] = 0.5 * np.sin(2 * np.pi * i / 96) + 0.5
    COS_TIMES[i] = 0.5 * np.cos(2 * np.pi * i / 96) + 0.5
    TIME_INTERVALS[(datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=15 * i)).strftime('%H:%M')] = i
for i, day in enumerate(DAYS_OF_WEEK):
    SIN_DAYS[day] = 0.5 * np.sin(2 * np.pi * i / 7) + 0.5
    COS_DAYS[day] = 0.5 * np.cos(2 * np.pi * i / 7) + 0.5
settings: {}
# Loads the settings into a dictionary
with open('config.json', 'r') as f:
    settings = json.load(f)


def get_setting(key):
    """ Gets a setting value

    Parameters:
        key  (String): the specific setting
    """
    return settings[key]


def convert_absolute_coordinates_to_relative(latitude, longitude):
    return latitude-RELATIVE_LAT, longitude-RELATIVE_LONG


def convert_direction_to_cyclic(direction):
    if isinstance(direction, int):
        return DIRECTIONS_SINE[direction-1], DIRECTIONS_COSINE[direction-1]
    elif direction == "N":
        return SIN_TIMES[0], COS_TIMES[0]
    elif direction == "NE":
        return SIN_TIMES[1], COS_TIMES[1]
    elif direction == "E":
        return SIN_TIMES[2], COS_TIMES[2]
    elif direction == "SE":
        return SIN_TIMES[3], COS_TIMES[3]
    elif direction == "S":
        return SIN_TIMES[4], COS_TIMES[4]
    elif direction == "SW":
        return SIN_TIMES[5], COS_TIMES[5]
    elif direction == "W":
        return SIN_TIMES[6], COS_TIMES[6]
    elif direction == "NW":
        return SIN_TIMES[7], COS_TIMES[7]


def convert_time_interval_to_cyclic(time):
    return SIN_TIMES[time], COS_TIMES[time]

def convert_time_to_cyclic(time):
    return SIN_TIMES[TIME_INTERVALS[time]], COS_TIMES[TIME_INTERVALS[time]]

def convert_date_to_cyclic_day(date):
    day, month, year = (int(x) for x in date.split('/'))
    day_of_week = datetime.date(year, month, day).strftime("%A")
    return SIN_DAYS[day_of_week], COS_DAYS[day_of_week]


class ConsoleStream(QtCore.QObject):
    """ Handles the system-specific functions for stdout """
    text_output = QtCore.pyqtSignal(str)

    def write(self, text):
        """ Writes to the EditText control

        Parameters:
            text  (String): text from the console output
        """
        self.text_output.emit(str(text))

    def flush(self):
        """ Does nothing, here so the compiler doesn't complain """
        pass
