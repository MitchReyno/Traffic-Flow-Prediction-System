import csv
import os
import queue

import pandas as pd

from data.data import get_time_between_points
from data.scats import ScatsData

SCATS_DATA = ScatsData()

ROAD_CONNECTIONS_FILE = "data/MappingData.xls"
DATA_FILE = "data/tfps.csv"

BIDIRECTIONAL_CONNECTIONS = True
ADD_ALL_DIRECTIONS = True


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
        # The currently selected time of day
        self.time = None
        # Rows of data about the time taken to travel between 2 SCATS locations
        self.time_data = pd.DataFrame()
        # Basic road connections
        self.roads = {}
        # Road connections with time taken to travel between them
        self.roads_data = {}

        # Initialise the data
        road_data_file = pd.read_excel(ROAD_CONNECTIONS_FILE, sheet_name='NodeConnections', skiprows=1)
        self.connections = pd.DataFrame(road_data_file)

        self.read_connections()
        self.load_travel_times()

    def load_travel_times(self):
        """ Loads the time to travel between SCATS locations """
        if os.path.exists(DATA_FILE):
            dataset = pd.read_csv(DATA_FILE, encoding="latin-1", sep=",", header=None)
            self.time_data = pd.DataFrame(dataset)

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
                        estimated_time = get_time_between_points(int(origin[0]), int(origin[1]),
                                                                 int(destination[0]), int(destination[1]), time_of_day)

                        writer.writerow([time_of_day, scats, road, str(estimated_time)])
                        print("Recorded time to travel between {0} and {1} at {2}".format(scats, road, time_of_day))

    def remove_connection(self, intersection1, intersection2):
        """ Removes a road connection

        Parameters:
            intersection1 (String): the base intersection
            intersection2 (String): the connected intersection to remove
        """
        try:
            if intersection2 in self.roads[intersection1]:
                self.roads[intersection1].remove(intersection2)
        except KeyError:
            pass

    def add_connection(self, intersection1, intersection2):
        """ Adds a road connection

        Parameters:
            intersection1 (String): the base intersection
            intersection2 (String): the connected intersection
        """
        try:
            if (intersection2 not in self.roads[intersection1]) and (intersection2 != intersection1):
                self.roads[intersection1].append(intersection2)
        except KeyError:
            self.roads[intersection1] = [intersection2]

    def add_internal_connections(self, location):
        """ Adds the direction connections to an intersection

        Parameters:
            location (String): the intersection
        """
        loc = location.split("-")
        directions = SCATS_DATA.get_scats_approaches(int(loc[0]))

        for direction in directions:
            intersection = "{0}-{1}".format(loc[0], direction)
            self.add_connection(location, intersection)

            if BIDIRECTIONAL_CONNECTIONS:
                self.add_connection(intersection, location)

    def read_connections(self):
        """ Reads the road connections from the mapping file """
        if not self.connections.empty:
            for row in self.connections.itertuples():
                intersection1 = row[2]
                intersection2 = row[3]

                self.add_connection(intersection1, intersection2)
                if ADD_ALL_DIRECTIONS:
                    self.add_internal_connections(intersection1)

                if BIDIRECTIONAL_CONNECTIONS:
                    self.add_connection(intersection2, intersection1)
                    if ADD_ALL_DIRECTIONS:
                        self.add_internal_connections(intersection2)

    def update_scats_time(self, time):
        """ Updates the weight (time) of each node for path finding

        Parameters:
            time (String): the time of day ##:##
        """
        raw_data = self.time_data.loc[(self.time_data[0] == time)]

        for i in raw_data.index:
            origin = raw_data[1].loc[i]
            destination = raw_data[2].loc[i]
            time_taken = raw_data[3].loc[i]

            key = "{0}:{1}".format(origin, destination)
            self.roads_data[key] = time_taken

        self.time = time

    def shortest_path(self, origin, destination, time):
        """ Returns the shortest path between intersections (using Dijkstra's algorithm)

        Parameters:
            origin (String): the origin scats site
            destination (String): the destination scats site
            time (String): the time value

        Returns:
            array: the path to one intersection from another
        """
        paths = {origin: (None, 0)}
        current_intersection = origin
        visited = set()

        while current_intersection != destination:
            visited.add(current_intersection)
            destinations = self.roads[current_intersection]
            time_to_intersection = paths[current_intersection][1]

            for next_destination in destinations:
                key = "{0}:{1}".format(current_intersection, next_destination)
                time_taken = self.roads_data[key] + time_to_intersection

                if next_destination not in paths:
                    paths[next_destination] = (current_intersection, time_taken)
                else:
                    shortest_time = paths[next_destination][1]
                    if shortest_time > time_taken:
                        paths[next_destination] = (current_intersection, time_taken)

            next_destinations = {i: paths[i] for i in paths if i not in visited}

            if not next_destinations:
                return None

            current_intersection = min(next_destinations, key=lambda k: next_destinations[k][1])

        path = []
        while current_intersection is not None:
            path.append(current_intersection)
            next_destination = paths[current_intersection][0]
            current_intersection = next_destination

        result = path[::-1]

        return result

    def path_cost(self, path):
        """ Calculates the total travel time given a path

        Parameters:
            path (array): the array of intersections

        Returns:
            int: the total cost / travel time
        """
        cost = 0
        for i in range(1, len(path)):
            start = path[i - 1]
            end = path[i]

            key = "{0}:{1}".format(start, end)
            cost += self.roads_data[key]

        return cost

    def route(self, o_scats, o_junction, d_scats, d_junction, time, number_of_paths):
        """ Finds a number of routes from the origin to the destination

        Parameters:
            o_scats (String): the origin scats site
            o_junction (String): the origin location
            d_scats (String): the destination scats site
            d_junction (String): the destination
            time (String): the time of day ##:##
            number_of_paths (int): the maximum number of routes to generate
        Returns:
            array: the routes
            array: the travel time for each route

        """
        if self.time != time:
            self.update_scats_time(time)

        origin = "{0}-{1}".format(o_scats, o_junction)
        destination = "{0}-{1}".format(d_scats, d_junction)

        a = [self.shortest_path(origin, destination, time)]
        a_costs = [self.path_cost(a[0])]
        b = queue.PriorityQueue()

        for k in range(1, number_of_paths):
            route_size = len(a[k - 1]) - 1

            for i in range(route_size):
                spur_node = a[k - 1][i]
                root_path = a[k - 1][:i]

                removed_roads = []

                for path in a:
                    if len(path) - 1 > i and root_path == path[:i]:
                        key = "{0}:{1}".format(path[i], path[i + 1])
                        travel_time = self.roads_data[key]

                        removed_roads.append((path[i], path[i + 1], travel_time))
                        self.remove_connection(path[i], path[i + 1])

                spur_path = self.shortest_path(spur_node, destination, time)

                if spur_path is not None:
                    total_path = root_path + spur_path
                    total_cost = self.path_cost(total_path)

                    b.put((total_cost, total_path))

                for removed_road in removed_roads:
                    # Add the road connection back into the list
                    start_intersection, end_intersection, time_taken = removed_road
                    self.add_connection(start_intersection, end_intersection)

                    # Add the time it takes to travel between the intersections
                    key = "{0}:{1}".format(start_intersection, end_intersection)
                    self.roads_data[key] = time_taken

            while True:
                new_route_cost, new_route = b.get()

                # Add only unique paths
                if new_route not in a:
                    a.append(new_route)
                    a_costs.append(new_route_cost)

                    break

        return a, a_costs

    def debug_print(self):
        """ Prints the connected roads list """
        print(self.roads)
