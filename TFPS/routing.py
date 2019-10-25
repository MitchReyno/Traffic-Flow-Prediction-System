import json
import csv
import os

import pandas as pd

from data.data import get_distance_between_points
from data.scats import ScatsData

SCATS_DATA = ScatsData()

ROAD_CONNECTIONS_FILE = "data/roads.json"
DATA_FILE = "data/tfps.csv"


def format_index_to_time(index):
    """ Converts an index into a time value

    Parameters:
        index (int): the value of the index

    Returns:
        String: the time value in the format ##:##
    """
    minutes = index * 15

    return '{:02d}:{:02d}'.format(*divmod(minutes, 60))


class Location(object):
    """ Contains the functionality for the routing capabilities """

    def __init__(self):
        with open(ROAD_CONNECTIONS_FILE, "r") as f:
            self.data = json.load(f)

        # The currently selected time of day
        self.time = None

        # Rows of data about the time taken to travel between 2 SCATS locations
        self.time_data = pd.DataFrame()

        # Basic road connections
        self.roads = {}

        # Road connections with time information
        self.roads_data = {}

        self.create_map()

        if os.path.exists(DATA_FILE):
            dataset = pd.read_csv(DATA_FILE, encoding="latin-1", sep=",", header=None)
            self.time_data = pd.DataFrame(dataset)
        else:
            self.generate_all_data()


    def generate_all_data(self):
        """ Writes all the trained time data to a CSV file """
        with open(DATA_FILE, "w", newline='') as f:
            writer = csv.writer(f)

            for i in range(96):
                for scats, roads in self.roads.items():
                    for road in roads:
                        origin = scats.split("-")
                        destination = road.split("-")

                        time_of_day = format_index_to_time(i)
                        estimated_time = get_distance_between_points(int(origin[0]), int(origin[1]),
                                                                 int(destination[0]), int(destination[1]))

                        writer.writerow([time_of_day, scats, road, str(estimated_time)])
                        writer.writerow([time_of_day, road, scats, str(estimated_time)])


    def create_map(self):
        """ Creates a mapping of connected SCATS locations """
        scats_numbers = SCATS_DATA.get_all_scats_numbers()

        for scats_number in scats_numbers:
            intersections = SCATS_DATA.get_scats_approaches(scats_number)

            for intersection in intersections:
                key = "{0}-{1}".format(scats_number, intersection)

                if key not in self.roads.keys():
                    self.roads[key] = []

                if key in self.data.keys():
                    connected_road = self.data[key]
                    self.roads[key].append(connected_road)

                    if connected_road not in self.roads.keys():
                        self.roads[connected_road] = []

                    if (connected_road in self.data.keys()) and (key not in self.roads[connected_road]):
                        self.roads[connected_road].append(key)

                for i in [i for i in intersections if i != intersection]:
                    self.roads[key].append("{0}-{1}".format(scats_number, i))

    def update_scats_time(self, time):
        """ Updates the weight (time) of each node for path finding

        Parameters:
            time (String): the time of day ##:##
        """
        raw_data = self.time_data.loc[(self.data[0] == time)]

        for row in raw_data:
            self.roads_data[(row[1], row[2])] = row[3]

        self.time = time

    def route(self, o_scats, o_junction, d_scats, d_junction, time):
        """ Returns an array of intersections from a given origin to destination

        Parameters:
            o_scats (int): the origin scats site
            o_junction (int): the origin location
            d_scats (int): the destination scats site
            d_junction (int): the destination
            time (String): the time of day ##:##

        Returns:
            array: the path to one intersection from another
        """
        if self.time != time:
            self.update_scats_time(time)

        origin = "{0}-{1}".format(o_scats, o_junction)
        destination = "{0}-{1}".format(d_scats, d_junction)

        paths = {origin: (None, 0)}
        current_intersection = origin
        visited = set()

        while current_intersection != destination:
            visited.add(current_intersection)
            destinations = self.roads[current_intersection]
            time_to_intersection = paths[current_intersection][1]

            for next_destination in destinations:
                time_taken = self.roads_data[(current_intersection, next_destination)] + time_to_intersection
                if next_destination not in paths:
                    paths[next_destination] = (current_intersection, time_taken)
                else:
                    shortest_time = paths[next_destination][1]
                    if shortest_time > time_taken:
                        paths[next_destination] = (current_intersection, time_taken)

            next_destinations = {i: paths[i] for i in paths if i not in visited}
            current_intersection = min(next_destinations, key=lambda k: next_destinations[k][1])

        path = []
        while current_intersection is not None:
            path.append(current_intersection)
            next_destination = paths[current_intersection][0]
            current_intersection = next_destination

        result = path[::-1]

        return result

    def debug_print(self, scats):
        """ Prints the connected roads/intersection for a given SCATS location

            Parameters:
                scats (int): the scats location
        """
        print(self.roads[scats])
