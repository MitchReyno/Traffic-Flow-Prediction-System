import pygame
import math
import pandas as pd
from routing import Location

from predictor import Predictor

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (250, 250, 250)
LIGHT_GRAY = (252, 252, 252)
MID_GRAY = (100, 100, 100)
DARKISH_GRAY = (70, 70, 70)
DARK_GRAY = (50, 50, 50)
BLUE_GRAY = (50, 50, 60)
GREEN_GRAY = (50, 60, 50)
RED_GRAY = (60, 50, 50)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 125, 0)
YELLOW = (255, 255, 0)
BROWN = (90, 65, 50)

OPTN_W = 200
SCRN_H = 790
SCRN_W = int((0.82484 * SCRN_H)) + OPTN_W

# Translates to the 'fidelity' of the traffic info 50 is ~16 lines from top to bottom.
MAX_LINE_SEGMENT_SIZE = 50

ALLOW_MAP_ADJUSTMENT = False
AUTOMATIC_ROAD_INFO = True
MINIMIZE_FOR_CONSOLE_INPUT = False

MAP_IMG = pygame.image.load("data/final_map.png")

MAP_OFFSET = [-154, 0]

LARGEST_NODE_INDEX = -1
LARGEST_CONNECTION_INDEX = -1

LOCATIONS = Location()

MENU = {
    0: "Journey Planner",
    1: "Add",
    2: "Connect",
    3: "Data"
}

SECTION_COLS = {
    "Menu": DARK_GRAY,
    "Add": GREEN_GRAY,
    "Connect": GREEN_GRAY,
    "Data": BLUE_GRAY,
    "Journey Planner": RED_GRAY
}

ADD_MODES = {
    0: "Menu",
    1: "Info",
    2: "Add SCAT",
    3: "Adjust Position",
    4: "Toggle Directions",
    5: "Add Details",
    6: "ModeInfo"
}

CONNECT_MODES = {
    0: "Menu",
    1: "Info",
    2: "Select",
    3: "Direction",
    4: "Target",
    5: "Remove Connection",
    6: "ModeInfo"
}

JOURNEY_MODES = {
    0: "Menu",
    1: "Start Point",
    2: "Destination",
    3: "Start Time",
    4: "Results",
    5: "Colour Coded Results",
    6: "ModeInfo"
}

DATA_MODES = {
    0: "Menu",
    1: "Accuracy Comparison",
    2: "Road Traffic",
    3: "Section Traffic",
    4: "Projected Node Traffic",
    5: "Actual Node Traffic",
    6: "ModeInfo"
}

def get_options(section):
    if section == "Add":
        return ADD_MODES
    if section == "Connect":
        return CONNECT_MODES
    if section == "Journey Planner":
        return JOURNEY_MODES
    if section == "Data":
        return  DATA_MODES
    return MENU


MODE_INFO = {
    "Menu": "Choose between adding points, connecting points, and mapping a journey.",
    "Info": "Safe mode for viewing map data. Click Select to start.",

    "Select": "Select a SCAT to add a connection from.",
    "Direction": "Select the direction of this connection.",
    "Target": "Select the target SCAT for this connection. The program will automatically find the best direction.",
    "Remove Connection": "Click a connection to select it, then press 'delete' to remove it.",

    "Add SCAT": "Click the map to choose the position of the new 'fake' SCAT.",
    "Adjust Position": "Use the arrow-keys to adjust the position of the SCAT.",
    "Toggle Directions": "Click to toggle whether the SCAT has a node in each direction.",
    "Add Details": "Type the name of each node in the console.",

    "Start Point": "Choose the first point of your journey by clicking on the map.",
    "Destination": "Choose your destination by clicking on the map.",
    "Start Time": "Enter the starting time in the console, so traffic can be predicted.",
    "Results": "The predicted best route should appear in RED on the map, and the next 4 best in BLUE.",
    "Colour Coded Results": "Showing the time cost (Red = High cost) of each road in the best route. INCOMPLETE",

    "Accuracy Comparison": "Shows the differences between predicted and actual traffic.",
    "Road Traffic": "Shows the predicted traffic for each road.",
    "Section Traffic": "Shows the predicted traffic for small sections of the road.",
    "Projected Node Traffic": "Hover over a node to see the predicted traffic for that road.",
    "Actual Node Traffic": "Hover over a node to see the data received for that node.",

    "None": "Click on an option to start.",

    "ModeInfo": "THIS TEXT SHOULD NOT BE USED."
}

NUM_OPTN = max(len(ADD_MODES), len(CONNECT_MODES), len(JOURNEY_MODES))

PREDICTOR = Predictor("model/deepfeedfwd/Generalised/Model.h5")


class SelectionInfo:
    def __init__(self):
        # Universal
        self.has_selection = False
        self.type = "None"
        self.section = "Journey Planner"
        self.mode = "Start Point"
        self.hover_mode = "none"
        self.chosen_time = "08:00"
        self.chosen_date = "23/10/2019"

        # Connecting
        self.node = None
        self.direction = None
        self.connector_node = None
        self.connection = None
        self.largest_connection_index = -1
        self.data_segments = None

        # Adding
        self.largest_node_index = -1

        # Journey
        self.start_node = None
        self.target_node = None
        self.path = []
        self.time = "12:30"
        self.day = 1


SELECTION = SelectionInfo()


class CardinalDir:
    @staticmethod
    def int_to_str(dir_as_int):
        if dir_as_int == 1:
            return "North"
        elif dir_as_int == 2:
            return "North-East"
        elif dir_as_int == 3:
            return "East"
        elif dir_as_int == 4:
            return "South-East"
        elif dir_as_int == 5:
            return "South"
        elif dir_as_int == 6:
            return "South-West"
        elif dir_as_int == 7:
            return "West"
        elif dir_as_int == 8:
            return "North-West"

    @staticmethod
    def int_to_short_str(dir_as_int):
        if dir_as_int == 1:
            return "N"
        elif dir_as_int == 2:
            return "NE"
        elif dir_as_int == 3:
            return "E"
        elif dir_as_int == 4:
            return "SE"
        elif dir_as_int == 5:
            return "S"
        elif dir_as_int == 6:
            return "SW"
        elif dir_as_int == 7:
            return "W"
        elif dir_as_int == 8:
            return "NW"

    @staticmethod
    def int_to_delta_pos(dir_as_int):
        if dir_as_int == 1:  # North
            return [0, -1]
        elif dir_as_int == 2:  # North-East
            return [1, -1]
        elif dir_as_int == 3:  # East
            return [1, 0.1]
        elif dir_as_int == 4:  # South-East
            return [1, 1]
        elif dir_as_int == 5:  # South
            return [0, 1]
        elif dir_as_int == 6:  # South-West
            return [-1, 1]
        elif dir_as_int == 7:  # West
            return [-1, -0.1]
        elif dir_as_int == 8:  # North-West
            return [-1, -1]

    @staticmethod
    def opposite_int(dir_as_int):
        opposite = (dir_as_int + 4) % 8
        if opposite == 0:
            opposite = 8
        return opposite

    @staticmethod
    def delta_pos_to_int(delta_pos):
        #      1
        #   8  |  2
        # 7  --+--  3
        #   6  |  4
        #      5
        # cardinal_dir = -1
        if abs(delta_pos[0]) > (abs(delta_pos[1]) * 2):
            if delta_pos[0] > 0:  # Close to x, x is positive: East
                cardinal_dir = 3
            else:  # Close to x, x is negative: West
                cardinal_dir = 7
        elif abs(delta_pos[1]) > (abs(delta_pos[0]) * 2):
            if delta_pos[1] > 0:  # Close to y, y is positive: South (inverted y-axis)
                cardinal_dir = 5
            else:  # Close to y, y is negative: North
                cardinal_dir = 1
        elif delta_pos[0] > 0:
            if delta_pos[1] > 0:  # x is positive, y is positive: South East
                cardinal_dir = 4
            else:  # x is positive, y is negative: North East
                cardinal_dir = 2
        else:
            if delta_pos[1] > 0:  # x is negative, y is positive: South West
                cardinal_dir = 6
            else:  # x is negative, y is negative: North West
                cardinal_dir = 8
        return cardinal_dir

    @staticmethod
    def pos_to_screen(pos, screen_width=SCRN_W, screen_height=SCRN_H, options_width=OPTN_W):
        min_lat = -37.8676
        max_lat = -37.78093
        min_long = 145.0083
        max_long = 145.09885
        lat_space = max_lat - min_lat
        long_space = max_long - min_long
        screen_x = ((pos[1] - min_long) / long_space) * (screen_width - options_width) + options_width
        screen_y = screen_height - (((pos[0] - min_lat) / lat_space) * screen_height)
        screen_pos = [int(screen_x), int(screen_y)]
        return screen_pos

    @staticmethod
    def apply_margins(pos, margin=None, screen_width=SCRN_W, screen_height=SCRN_H, options_width=OPTN_W):
        if margin is None:
            margin = [0, 0]
        if pos[0] < options_width + margin[0]:
            pos[0] = options_width + margin[0]
        elif pos[0] > screen_width - margin[0]:
            pos[0] = screen_width - margin[0]
        if pos[1] < 0 + margin[1]:
            pos[1] = 0 + margin[1]
        elif pos[1] > screen_height - margin[1]:
            pos[1] = screen_height - margin[1]
        return pos


class DirNode:
    def __init__(self, parent, node_name, position, direction):
        self.SCAT = parent
        self.name = node_name
        self.pos = position
        self.dir = direction


class SCATNode:
    def __init__(self, number):
        self.SCAT_number = number
        self.directions = []
        self.avg_pos = [-37, 145]

    def add_dir(self, new_dir):
        self.directions.append(new_dir)

    def calculate_pos(self):
        self.avg_pos = [0, 0]
        count = 0
        for node in self.directions:
            self.avg_pos[0] += node.pos[0]
            self.avg_pos[1] += node.pos[1]
            count += 1
        self.avg_pos[0] = self.avg_pos[0] / count
        self.avg_pos[1] = self.avg_pos[1] / count


# Describes the connections between MappingNodes, including their max speed.
class Connection:
    def __init__(self, id=-1, node_a=None, node_b=None, speed=60, name=""):
        self.id = id
        self.node_a = node_a
        self.node_b = node_b
        self.speed = speed
        self.name = name


class Segment:
    def __init__(self, pos_a, pos_b, traffic=0, max_traffic=1):
        self.pos_a = pos_a
        self.pos_b = pos_b  # [pos_a[0] + delta[0], pos_a[1] + delta[1]]
        self.traffic = traffic
        self.colour = (0, 0, 255)
        print("Created segment between ({0}, {1}) and ({2}, {3}) with traffic {4}".format(pos_a[0], pos_a[1], pos_b[0], pos_b[1], traffic))

    @staticmethod
    def generate_colour(traffic, max_traffic):
        green = int(max(0.0, min(255.0, 512.0 - ((float(traffic) / float(max_traffic)) * 512.0))))
        red = int(max(0.0, min(255.0, (float(traffic) / float(max_traffic)) * 512.0)))
        colour = (red, green, 0)
        print(colour)
        return colour

    def create_colour_using_max_traffic(self, max_traffic):
        self.colour = self.generate_colour(self.traffic, max_traffic)


# Draw the map, scats and nodes (scat directions), and connections.
def draw_common(screen, nodes, data_connections, draw_scats=True, draw_directions=True, draw_conns=True):
    screen.fill(WHITE)
    screen.blit(MAP_IMG, (OPTN_W + MAP_OFFSET[0], MAP_OFFSET[1]))
    if draw_scats:
        node_rep_size = 5
        for node in nodes:
            screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
            pygame.draw.circle(screen, GREEN, screen_pos, node_rep_size, 1)
            if draw_directions:
                for scat in node.directions:
                    screen_pos = CardinalDir.pos_to_screen(scat.pos)
                    pygame.draw.circle(screen, BLUE, screen_pos, node_rep_size, 1)

    if draw_conns:
        draw_connections(screen, data_connections, True)

    draw_buttons(screen)


def draw_connections(screen, data_connections, draw_traffic=False):
    if not draw_traffic:
        for conn in data_connections:
            pos_a = CardinalDir.pos_to_screen(conn.node_a.pos)
            pos_b = CardinalDir.pos_to_screen(conn.node_b.pos)
            pygame.draw.line(screen, RED, pos_a, pos_b, 2)
    else:
        if SELECTION.data_segments is not None:
            for segment in SELECTION.data_segments:
                pygame.draw.line(screen, segment.colour, segment.pos_a, segment.pos_b, 2)
        else:
            print("Segments don't exist, getting them.")
            generate_weighted_connections(data_connections, True)


def generate_weighted_connections(data_connections, split_lines=True):
    segments = []
    max_traffic = 0
    for conn in data_connections:
        # Use screen positions to calculate number of segments because coords are not normalised
        pos_a_screen = CardinalDir.pos_to_screen(conn.node_a.pos)
        pos_b_screen = CardinalDir.pos_to_screen(conn.node_b.pos)
        screen_delta = [pos_b_screen[0] - pos_a_screen[0], pos_b_screen[1] - pos_a_screen[1]]
        dist = math.sqrt(math.pow(screen_delta[0], 2) + math.pow(screen_delta[1], 2))
        num_segments = math.ceil(dist / MAX_LINE_SEGMENT_SIZE)
        print("Got {0} from {1} and {2}".format(num_segments, dist, MAX_LINE_SEGMENT_SIZE))
        direction = CardinalDir.delta_pos_to_int(screen_delta)

        pos_a = conn.node_a.pos
        pos_b = conn.node_b.pos
        delta = [pos_b[0] - pos_a[0], pos_b[1] - pos_a[1]]
        d = [delta[0] / num_segments, delta[1] / num_segments]
        #print("Delta = ({0}, {1})".format(delta[0], delta[1]))
        if not split_lines:
            #traffic = 5  # TEST VALUE
            traffic = get_traffic(pos_a[0], pos_a[1], direction, SELECTION.chosen_time, SELECTION.chosen_date)
            screen_start = CardinalDir.pos_to_screen(pos_a)
            screen_end = CardinalDir.pos_to_screen(pos_b)
            segment = Segment(screen_start, screen_end, traffic)
            segments.append(segment)
            max_traffic = max(max_traffic, traffic)

            # Reverse line with offset:
            # traffic = 5  # TEST VALUE
            traffic = get_traffic(pos_a[0], pos_a[1], direction, SELECTION.chosen_time, SELECTION.chosen_date)
            screen_start = CardinalDir.pos_to_screen(pos_b)
            screen_start = [screen_start[0] + 1, screen_start[1] + 1]
            screen_end = CardinalDir.pos_to_screen(pos_a)
            screen_end = [screen_end[0] + 1, screen_end[1] + 1]
            segment = Segment(screen_start, screen_end, traffic)
            segments.append(segment)
            max_traffic = max(max_traffic, traffic)
        else:
            start_pos = pos_a
            for i in range(num_segments):
                # traffic = i  # TEST VALUE
                traffic = get_traffic(pos_a[0], pos_a[1], direction, SELECTION.chosen_time, SELECTION.chosen_date)
                screen_start = CardinalDir.pos_to_screen(start_pos)
                start_pos = [start_pos[0] + d[0], start_pos[1] + d[1]]
                screen_end = CardinalDir.pos_to_screen(start_pos)
                segment = Segment(screen_start, screen_end, float(traffic))
                segments.append(segment)
                max_traffic = max(max_traffic, traffic)

            direction = CardinalDir.opposite_int(direction)
            start_pos = pos_b
            for i in range(num_segments):
                #traffic = i  # TEST VALUE
                traffic = get_traffic(pos_a[0], pos_a[1], direction, SELECTION.chosen_time, SELECTION.chosen_date)
                screen_start = CardinalDir.pos_to_screen(start_pos)
                screen_start = [screen_start[0] + 2, screen_start[1] + 2]
                start_pos = [start_pos[0] - d[0], start_pos[1] - d[1]]
                screen_end = CardinalDir.pos_to_screen(start_pos)
                screen_end = [screen_end[0] + 2, screen_end[1] + 2]
                segment = Segment(screen_start, screen_end, float(traffic))
                segments.append(segment)
                max_traffic = max(max_traffic, traffic)

        max_traffic = 0.280
        for segment in segments:
            segment.create_colour_using_max_traffic(max_traffic)
        SELECTION.data_segments = segments


def get_traffic(latitude, longitude, direction, time, date):

    inputs = [{
        "latitude": latitude,
        "longitude": longitude,
        "direction": CardinalDir.int_to_short_str(direction),
        "time": time,
        "date": date
    }]
    prediction = PREDICTOR.make_prediction(inputs)
    print(prediction[0])
    return prediction[0]
    # Use this to give the code (generate_weighted_connections) a traffic prediction for the specified point.
    # Should return a number (int ok but float better).
    # The algorithm will automatically find the maximum and generate colours which represent the range.


def render_text_multi_lines(screen, pos, string, max_length=20, text_size=12):
    words = string.split(" ")
    sub_string = ""
    lines = []
    for sub in words:
        if len(sub_string) + len(sub) + 1 < max_length:
            sub_string += sub + " "
        else:
            lines.append(sub_string)
            sub_string = sub + " "
    lines.append(sub_string)

    font = pygame.font.Font('freesansbold.ttf', text_size)
    i = 0
    for line in lines:
        text = font.render(line, True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = [pos[0], pos[1] - (text_size * (len(lines) / 2)) + ((text_size + 1) * i)]
        screen.blit(text, text_rect)
        i += 1


def draw_buttons(screen):
    mode = SELECTION.mode
    hover_mode = SELECTION.hover_mode
    font = pygame.font.Font('freesansbold.ttf', 12)

    col = SECTION_COLS[SELECTION.section]
    MODES = get_options(SELECTION.section)
    pygame.draw.rect(screen, col, (0, 0, OPTN_W, SCRN_H))

    for index in range(len(MODES)):
        # Draw button divider.
        pygame.draw.rect(screen, GRAY, (0, (index + 1) * (SCRN_H / NUM_OPTN), OPTN_W, 1))

        button_y = (SCRN_H / NUM_OPTN) * index
        if MODES[index] == "ModeInfo":
            render_text_multi_lines(screen, [OPTN_W / 2, button_y + (SCRN_H / NUM_OPTN / 2)], MODE_INFO[mode], 30)
            continue
        elif MODES[index] == mode:
            pygame.draw.rect(screen, MID_GRAY, (0, button_y, OPTN_W, SCRN_H / NUM_OPTN))
            text = font.render(mode, True, WHITE)
        elif MODES[index] == hover_mode:
            pygame.draw.rect(screen, DARKISH_GRAY, (0, button_y, OPTN_W, SCRN_H / NUM_OPTN))
            text = font.render(hover_mode, True, WHITE)
        else:
            text = font.render(MODES[index], True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = [OPTN_W / 2, button_y + (SCRN_H / NUM_OPTN / 2)]
        screen.blit(text, text_rect)


def draw_in_info_mode(screen, data_nodes, mouse_pos, hover_text=True):
    closest = 1000
    chosen_scat = data_nodes[0]
    for node in data_nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < 1:
            chosen_scat = node
            break
        elif dist < closest:
            chosen_scat = node
            closest = dist
    screen_pos = CardinalDir.pos_to_screen(chosen_scat.avg_pos)
    pygame.draw.circle(screen, RED, screen_pos, 15, 1)
    closest = 1000
    chosen_node = chosen_scat.directions[0]
    for scat in chosen_scat.directions:
        screen_pos = CardinalDir.pos_to_screen(scat.pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < closest:
            chosen_node = scat
            closest = dist

    if hover_text:
        text_pos = CardinalDir.pos_to_screen(chosen_node.pos)
        text_pos[1] -= 30
        text_pos = CardinalDir.apply_margins(text_pos, [20, 50])
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render("{0}: {1}".format(chosen_scat.SCAT_number, chosen_node.name), True, BLACK, YELLOW)
        text_rect = text.get_rect()
        text_rect.center = text_pos
        screen.blit(text, text_rect)
        text = font.render("Lat: {0}, Long: {1}".format(chosen_node.pos[0], chosen_node.pos[1]), True, BLACK, ORANGE)
        text_rect = text.get_rect()
        coords_pos = text_pos
        coords_pos[1] += 12
        text_rect.center = coords_pos
        screen.blit(text, text_rect)

    pygame.display.flip()


def select_mode_click(data_nodes, mouse_pos):
    closest = 1000
    chosen_scat = data_nodes[0]
    for node in data_nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < 5:
            chosen_scat = node
            break
        elif dist < closest:
            chosen_scat = node
            closest = dist
    SELECTION.has_selection = True
    SELECTION.type = "SCAT"
    SELECTION.node = chosen_scat
    SELECTION.mode = "Direction"
    print("SCAT number: {0} - ({1}, {2})".format(chosen_scat.SCAT_number,
                                                 chosen_scat.avg_pos[0], chosen_scat.avg_pos[1]))


def draw_in_select_mode(screen, data_nodes, mouse_pos, hover_text=False):
    closest = 1000
    chosen_scat = data_nodes[0]
    for node in data_nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < 5:
            chosen_scat = node
            break
        elif dist < closest:
            chosen_scat = node
            closest = dist
    screen_pos = CardinalDir.pos_to_screen(chosen_scat.avg_pos)
    pygame.draw.circle(screen, GREEN, screen_pos, 15, 1)
    closest = 1000
    chosen_node = chosen_scat.directions[0]
    for scat in chosen_scat.directions:
        screen_pos = CardinalDir.pos_to_screen(scat.pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < closest:
            chosen_node = scat
            closest = dist

    if hover_text:
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render(chosen_node.name, True, BLACK, YELLOW)
        text_rect = text.get_rect()
        text_rect.center = CardinalDir.pos_to_screen(chosen_node.pos)
        screen.blit(text, text_rect)
        text = font.render("Lat: {0}, Long: {1}".format(chosen_node.pos[0], chosen_node.pos[1]), True, BLACK, ORANGE)
        text_rect = text.get_rect()
        coords_pos = CardinalDir.pos_to_screen(chosen_node.pos)
        coords_pos[1] += 12
        text_rect.center = coords_pos
        screen.blit(text, text_rect)

    pygame.display.flip()


def direction_mode_click(mouse_pos):
    if SELECTION.has_selection and SELECTION.type == "SCAT":

        node_pos = CardinalDir.pos_to_screen(SELECTION.node.avg_pos)
        node_pos = CardinalDir.apply_margins(node_pos, [20, 50])
        delta_mouse = [mouse_pos[0] - node_pos[0], mouse_pos[1] - node_pos[1]]
        mouse_dir = CardinalDir.delta_pos_to_int(delta_mouse)

        for direction in SELECTION.node.directions:
            if mouse_dir == direction.dir:
                SELECTION.type = "Direction"
                SELECTION.direction = direction
                SELECTION.mode = "Target"


def draw_in_direction_mode(screen, data_nodes, mouse_pos):
    if SELECTION.has_selection and SELECTION.type == "SCAT":
        font = pygame.font.Font('freesansbold.ttf', 12)

        node_pos = CardinalDir.pos_to_screen(SELECTION.node.avg_pos)
        node_pos = CardinalDir.apply_margins(node_pos, [20, 50])
        pygame.draw.circle(screen, RED, node_pos, 10, 1)
        delta_mouse = [mouse_pos[0] - node_pos[0], mouse_pos[1] - node_pos[1]]
        mouse_dir = CardinalDir.delta_pos_to_int(delta_mouse)

        for direction in SELECTION.node.directions:
            node_pos = CardinalDir.pos_to_screen(SELECTION.node.avg_pos)
            rel_pos = CardinalDir.int_to_delta_pos(direction.dir)
            node_pos[0] = int(node_pos[0] + rel_pos[0] * 60)
            node_pos[1] = int(node_pos[1] + rel_pos[1] * 30)
            node_pos = CardinalDir.apply_margins(node_pos, [20, 50])

            pygame.draw.circle(screen, BLUE, node_pos, 5, 1)

        for direction in SELECTION.node.directions:
            if mouse_dir == direction.dir:
                node_pos = CardinalDir.pos_to_screen(SELECTION.node.avg_pos)
                rel_pos = CardinalDir.int_to_delta_pos(direction.dir)
                node_pos[0] = int(node_pos[0] + rel_pos[0] * 60)
                node_pos[1] = int(node_pos[1] + rel_pos[1] * 30)
                node_pos = CardinalDir.apply_margins(node_pos, [20, 50])

                text = font.render(direction.name, True, BLACK, GREEN)
                text_rect = text.get_rect()
                text_rect.center = node_pos
                screen.blit(text, text_rect)

    pygame.display.flip()


def target_mode_click(screen, data_nodes, data_connections, mouse_pos):
    closest = 1000
    chosen_scat = data_nodes[0]
    for node in data_nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < 5:
            chosen_scat = node
            break
        elif dist < closest:
            chosen_scat = node
            closest = dist

    SELECTION.has_selection = True
    SELECTION.type = "Connection"
    SELECTION.connection = chosen_scat
    SELECTION.mode = "Select"

    print("Finding best direction for connection.")
    origin_pos = CardinalDir.pos_to_screen(SELECTION.direction.pos)
    target_pos = CardinalDir.pos_to_screen(chosen_scat.avg_pos)
    delta_pos = [origin_pos[0] - target_pos[0], origin_pos[1] - target_pos[1]]  # Get opposite direction.
    connection_dir = CardinalDir.delta_pos_to_int(delta_pos)
    target_node = chosen_scat.directions[0]
    closest_dir = -1
    for direction in chosen_scat.directions:
        if direction.dir == connection_dir:
            target_node = direction
            break
        elif abs(connection_dir - direction.dir) < abs(connection_dir - closest_dir):
            target_node = direction
            closest_dir = direction.dir
    if closest_dir == target_node.dir:
        print("Perfect direction missing, using next best.")

    if MINIMIZE_FOR_CONSOLE_INPUT:
        pygame.display.iconify()
    else:
        font = pygame.font.Font('freesansbold.ttf', 40)
        text = font.render("ENTER DETAILS IN CONSOLE", True, BLACK, GREEN)
        text_rect = text.get_rect()
        text_rect.center = [int(SCRN_W / 2), int(SCRN_H / 2)]
        screen.blit(text, text_rect)
        pygame.display.flip()

    name = SELECTION.direction.name
    speed = 60
    print(">>Creating connection between '{0}' and '{1}'<<".format(SELECTION.direction.name, target_node.name))
    if not AUTOMATIC_ROAD_INFO:
        name = input("Type the name of this road, or leave blank to cancel:")
        if name == "":
            return
        speed = int(input("Type the speed limit of this road in k/h, or '0' to cancel:"))
        if speed == 0:
            return
    connection = Connection(SELECTION.largest_connection_index + 1, SELECTION.direction, target_node, speed, name)
    SELECTION.largest_connection_index += 1
    data_connections.append(connection)
    write_connection_data(data_connections)


def draw_in_target_mode(screen, data_nodes, mouse_pos, hover_text=True):
    if not SELECTION.has_selection or SELECTION.type != "Direction":
        return

    node_pos = CardinalDir.pos_to_screen(SELECTION.direction.pos)
    pygame.draw.circle(screen, RED, node_pos, 5, 1)

    closest = 1000
    chosen_scat = data_nodes[0]
    for node in data_nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < 5:
            chosen_scat = node
            break
        elif dist < closest:
            chosen_scat = node
            closest = dist

    origin_pos = CardinalDir.pos_to_screen(SELECTION.direction.pos)
    target_pos = CardinalDir.pos_to_screen(chosen_scat.avg_pos)
    delta_pos = [origin_pos[0] - target_pos[0], origin_pos[1] - target_pos[1]]  # Get opposite direction.
    connection_dir = CardinalDir.delta_pos_to_int(delta_pos)
    target_node = chosen_scat.directions[0]
    closest_dir = -1
    for direction in chosen_scat.directions:
        if direction.dir == connection_dir:
            target_node = direction
            break
        elif abs(connection_dir - direction.dir) < abs(connection_dir - closest_dir):
            target_node = direction
            closest_dir = direction.dir

    screen_pos = CardinalDir.pos_to_screen(target_node.pos)
    pygame.draw.line(screen, RED, node_pos, screen_pos, 2)
    pygame.draw.circle(screen, GREEN, screen_pos, 15, 1)

    if hover_text:
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render(target_node.name, True, BLACK, YELLOW)
        text_rect = text.get_rect()
        text_rect.center = CardinalDir.pos_to_screen(target_node.pos)
        screen.blit(text, text_rect)

        text = font.render("Lat: {0}, Long: {1}".format(target_node.pos[0], target_node.pos[1]), True, BLACK,
                           ORANGE)
        text_rect = text.get_rect()
        coords_pos = CardinalDir.pos_to_screen(target_node.pos)
        coords_pos[1] += 13
        text_rect.center = coords_pos
        screen.blit(text, text_rect)

        if connection_dir != CardinalDir.opposite_int(SELECTION.direction.dir):
            text = font.render("WARNING: STRANGE CONNECTION!", True, BLACK, RED)
            text_rect = text.get_rect()
            coords_pos = CardinalDir.pos_to_screen(target_node.pos)
            coords_pos[1] += 26
            text_rect.center = coords_pos
            screen.blit(text, text_rect)

    pygame.display.flip()


# Journey mode functions:

def choose_point_click(data_nodes, mouse_pos):
    closest = 1000
    chosen_scat = data_nodes[0]
    for node in data_nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < 1:
            chosen_scat = node
            break
        elif dist < closest:
            chosen_scat = node
            closest = dist
    closest = 1000
    chosen_node = chosen_scat.directions[0]
    for scat in chosen_scat.directions:
        screen_pos = CardinalDir.pos_to_screen(scat.pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < closest:
            chosen_node = scat
            closest = dist

    if SELECTION.mode == "Start Point":
        SELECTION.has_selection = True
        SELECTION.start_node = chosen_node
        SELECTION.mode = "Destination"
    elif SELECTION.mode == "Destination":
        SELECTION.has_selection = True
        SELECTION.target_node = chosen_node
        SELECTION.mode = "Start Time"


def draw_in_choose_point_mode(screen, data_nodes, mouse_pos, hover_text=True):
    closest = 1000
    chosen_scat = data_nodes[0]
    col = RED
    if SELECTION.mode == "Destination" and SELECTION.start_node is not None:
        screen_pos = CardinalDir.pos_to_screen(SELECTION.start_node.pos)
        pygame.draw.circle(screen, col, screen_pos, 15, 2)
        col = BLUE

    for node in data_nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < 1:
            chosen_scat = node
            break
        elif dist < closest:
            chosen_scat = node
            closest = dist
    screen_pos = CardinalDir.pos_to_screen(chosen_scat.avg_pos)
    pygame.draw.circle(screen, col, screen_pos, 15, 1)
    closest = 1000
    chosen_node = chosen_scat.directions[0]
    for scat in chosen_scat.directions:
        screen_pos = CardinalDir.pos_to_screen(scat.pos)
        dist = math.sqrt(math.pow(abs(mouse_pos[0] - screen_pos[0]), 2) +
                         math.pow(abs(mouse_pos[1] - screen_pos[1]), 2))
        if dist < closest:
            chosen_node = scat
            closest = dist

    if hover_text:
        text_pos = CardinalDir.pos_to_screen(chosen_node.pos)
        text_pos[1] -= 30
        text_pos = CardinalDir.apply_margins(text_pos, [20, 50])
        font = pygame.font.Font('freesansbold.ttf', 12)
        text = font.render(chosen_node.name, True, BLACK, YELLOW)
        text_rect = text.get_rect()
        text_rect.center = text_pos
        screen.blit(text, text_rect)
        text = font.render("Lat: {0}, Long: {1}".format(chosen_node.pos[0], chosen_node.pos[1]), True, BLACK, ORANGE)
        text_rect = text.get_rect()
        coords_pos = text_pos
        coords_pos[1] += 12
        text_rect.center = coords_pos
        screen.blit(text, text_rect)

    pygame.display.flip()


def time_change(up=True):
    time = SELECTION.time.split(":")
    hour = int(time[0])
    mins = int(time[1])
    if up:
        if mins == 45:
            mins = 0
            hour += 1
            if hour == 24:
                hour = 0
        else:
            mins += 15
    else:
        if mins == 0:
            mins = 45
            hour -= 1
            if hour == -1:
                hour = 23
        else:
            mins -= 15
    txt_mins = str(mins)
    if mins == 0:
        txt_mins = "00"
    txt_hour = str(hour)
    if hour < 10:
        txt_hour = "0" + txt_hour
    SELECTION.time = "{0}:{1}".format(txt_hour, txt_mins)


def time_mode_click(data_nodes, data_connections, mouse_pos):
    # If mouse is at the top of the screen increase time.
    if mouse_pos[1] < SCRN_H / 3:
        time_change(True)
    # If mouse is in center of screen continue to drawing path.
    elif mouse_pos[1] < (SCRN_H / 3) * 2:
        get_path(data_nodes, data_connections)
        SELECTION.mode = "Results"
    # If mouse is at the bottom of the screen decrease time.
    else:
        time_change(False)


def draw_in_time_mode(screen, mouse_pos):
    col = GREEN

    # If mouse is at the top of the screen highlight 'increase'.
    if mouse_pos[1] < SCRN_H / 3:
        col = BLUE
    else:
        col = GREEN
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("^ +15 mins ^", True, col, DARK_GRAY)
    text_rect = text.get_rect()
    text_rect.center = [int(SCRN_W / 2) + OPTN_W, int(SCRN_H / 4)]
    screen.blit(text, text_rect)

    # Draw the current time
    col = WHITE
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("Time: {0}".format(SELECTION.time), True, col, DARK_GRAY)
    text_rect = text.get_rect()
    text_rect.center = [int(SCRN_W / 2) + OPTN_W, int(SCRN_H / 2) - 32]
    screen.blit(text, text_rect)

    # If mouse is in center of screen highlight 'continue'.
    if SCRN_H / 3 < mouse_pos[1] < (SCRN_H / 3) * 2:
        col = BLUE
    else:
        col = WHITE
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("> Calculate best journey <", True, col, DARK_GRAY)
    text_rect = text.get_rect()
    text_rect.center = [int(SCRN_W / 2) + OPTN_W, int(SCRN_H / 2) + 32]
    screen.blit(text, text_rect)

    # If mouse is at the bottom of the screen highlight 'increase'.
    if mouse_pos[1] > (SCRN_H / 3) * 2:
        col = BLUE
    else:
        col = RED
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("v -15 mins v", True, col, DARK_GRAY)
    text_rect = text.get_rect()
    text_rect.center = [int(SCRN_W / 2) + OPTN_W, int((SCRN_H / 4) * 3)]
    screen.blit(text, text_rect)

    pygame.display.flip()


def enter_start_time(screen, data_nodes, data_connections):
    if MINIMIZE_FOR_CONSOLE_INPUT:
        pygame.display.iconify()
    else:
        font = pygame.font.Font('freesansbold.ttf', 40)
        text = font.render("ENTER DETAILS IN CONSOLE", True, BLACK, GREEN)
        text_rect = text.get_rect()
        text_rect.center = [int(SCRN_W / 2), int(SCRN_H / 2)]
        screen.blit(text, text_rect)
        pygame.display.flip()

    print(">>Journey between '{0}' and '{1}'<<".format(SELECTION.start_node.name, SELECTION.target_node.name))
    time = input("Enter the start time for the journey as 'H:M', or leave blank to cancel: ")
    if time == "":
        SELECTION.mode = "Destination"
        return

    get_path(data_nodes, data_connections)


def get_path(data_nodes, data_connections):
    # The selected start/end of the journey, as a reference to a node object (which is a single 'direction' of a SCAT).
    start_node = SELECTION.start_node
    target_node = SELECTION.target_node
    time = SELECTION.time

    start = start_node.SCAT.SCAT_number
    start_intersection = start_node.dir

    end = target_node.SCAT.SCAT_number
    end_intersection = target_node.dir

    #path = LOCATIONS.route(start, start_intersection, end, end_intersection, time)
    # TEST PATH:
    path = ["4043-1", "4040-3", "3804-1", "3122-5"]

    tuple_path = []
    connection_a = None
    skip_first = True
    for str_node in path:
        tuple_node = str_node.split("-")
        if not skip_first:
            tuple_path.append([connection_a, tuple_node])
        else:
            skip_first = False
        connection_a = tuple_node

    conn_path = []
    for conn in tuple_path:
        connection = Connection()
        connection.id = -1
        node_a_info = conn[0]
        for node in data_nodes:
            if node_a_info[0] == str(node.SCAT_number):
                for direction in node.directions:
                    if node_a_info[1] == str(direction.dir):
                        connection.node_a = direction
                        break

        node_b_info = conn[1]
        for node in data_nodes:
            if node_b_info[0] == str(node.SCAT_number):
                for direction in node.directions:
                    if node_b_info[1] == str(direction.dir):
                        connection.node_b = direction
                        break

        conn_path.append(connection)
    SELECTION.path = conn_path


def draw_path(screen):
    pos_b = [0, 0]
    for conn in SELECTION.path:
        pos_a = CardinalDir.pos_to_screen(conn.node_a.pos)
        pos_b = CardinalDir.pos_to_screen(conn.node_b.pos)
        pygame.draw.line(screen, RED, pos_a, pos_b, 2)
        pygame.draw.circle(screen, BLUE, pos_a, 3, 3)
    pygame.draw.circle(screen, GREEN, pos_b, 3, 3)

    pygame.display.flip()


# Convert the excel cell data into nodes as objects.
def format_nodes(data):
    node_list = []
    last_scat = -1
    scat_node = SCATNode(-1)
    for row in data:
        if row[1] != last_scat:
            if last_scat != -1:
                scat_node.calculate_pos()
                node_list.append(scat_node)
            scat_node = SCATNode(row[1])
            last_scat = row[1]
        pos = [row[3], row[4]]
        dir_node = DirNode(scat_node, row[2], pos, row[5])
        scat_node.add_dir(dir_node)
    return node_list


def print_formatted_nodes(nodes):
    print(">>>>> Formatted Nodes <<<<<")
    for node in nodes:
        print("SCAT: {0}, avg coords: ({1}, {2}), num dirs: {3}".format(node.SCAT_number, node.avg_pos[0],
                                                                        node.avg_pos[1], len(node.directions)))
        for dir_node in node.directions:
            print("----Dir: {0}, '{1}', coords: ({2}, {3})".format(dir_node.dir, dir_node.name,
                                                                   dir_node.pos[0], dir_node.pos[1]))


def get_node_data(print_raw=False, print_formatted=False):
    # Get nodes from excel sheet
    data = "data/ScatsNodeData.xls"
    panda_nodes = pd.read_excel(data, sheet_name='Data', nrows=142)
    nodes = pd.DataFrame(panda_nodes)

    if print_raw:
        for row in nodes.itertuples():
            print("[{0}] Scat {1}: {2}, coords({3}, {4}), dir = {5}".format(row[0], row[1], row[2], row[3], row[4],
                                                                            CardinalDir.int_to_short_str(row[5])))

    formatted_nodes = format_nodes(nodes.itertuples())
    if print_formatted:
        print_formatted_nodes(formatted_nodes)

    return formatted_nodes


def print_formatted_connections(connections):
    print("Formatted Connections:")
    for c in connections:
        print("ID={0}, Node A: {1}, Node B: {2}, speed: {3}, name: {4}".format(c.id, c.node_a.name, c.node_b.name,
                                                                               c.speed, c.name))


def format_connections(connections, data_nodes):
    connection_list = []
    for row in connections.itertuples():
        if row[1] == "":
            break

        connection = Connection()
        connection.id = row[1]
        SELECTION.largest_connection_index = row[1]
        node_a_info = row[2].split("-")
        for node in data_nodes:
            if node_a_info[0] == str(node.SCAT_number):
                for direction in node.directions:
                    if node_a_info[1] == str(direction.dir):
                        connection.node_a = direction
                        break

        node_b_info = row[3].split("-")
        for node in data_nodes:
            if node_b_info[0] == str(node.SCAT_number):
                for direction in node.directions:
                    if node_b_info[1] == str(direction.dir):
                        connection.node_b = direction

        connection.speed = row[4]
        connection.name = row[5]

        connection_list.append(connection)

    return connection_list


def get_connection_data(data_nodes, print_raw=False, print_formatted=False):
    # Get nodes from excel sheet
    data = "data/MappingData.xls"
    panda_connections = pd.read_excel(data, sheet_name='NodeConnections')
    connections = pd.DataFrame(panda_connections)

    print("Connections:")
    if print_raw:
        for row in connections.itertuples():
            print("[{0}] ID={1}, Node A: {2}, Node B: {3}, Speed Limit: {4}, Name: {5}".format(row[0], row[1], row[2],
                                                                                               row[3], row[4], row[5]))

    formatted_connections = format_connections(connections, data_nodes)
    if print_formatted:
        print_formatted_connections(formatted_connections)

    return formatted_connections


def write_connection_data(data_connections):
    data = []
    for connection in data_connections:
        node_a = str(connection.node_a.SCAT.SCAT_number) + "-" + str(connection.node_a.dir)
        node_b = str(connection.node_b.SCAT.SCAT_number) + "-" + str(connection.node_b.dir)
        connection_as_list = [connection.id, node_a, node_b, connection.speed, connection.name]
        data.append(connection_as_list)
    framed_data = pd.DataFrame(data)
    framed_data.to_excel("data/MappingData.xls", sheet_name="NodeConnections", index=False)


def find_simple_connections(data_nodes, data_connections):
    for scat in data_nodes:
        for direction in scat.directions:
            card_dir = CardinalDir.opposite_int(direction.dir)
            closest = 10000
            chosen_node = None
            # For each node, search the other nodes for the closest one that is in the opposite direction.
            for scat_2 in data_nodes:
                for direction_2 in scat_2.directions:
                    if direction_2.dir == card_dir:
                        origin_pos = CardinalDir.pos_to_screen(direction.pos)
                        dest_pos = CardinalDir.pos_to_screen(direction_2.pos)
                        delta_pos = [dest_pos[0] - origin_pos[0], dest_pos[1] - origin_pos[1]]
                        if CardinalDir.delta_pos_to_int(delta_pos) == direction.dir:
                            squared_dist = math.pow(dest_pos[0] - origin_pos[0], 2) + math.pow(dest_pos[1] - origin_pos[1], 2)
                            if squared_dist < closest:
                                closest = squared_dist
                                chosen_node = direction_2
            if chosen_node is not None:
                already_exists = False
                for connection in data_connections:
                    if (connection.node_a in {chosen_node, direction}) and (connection.node_b in {chosen_node, direction}):
                        already_exists = True
                        break
                if not already_exists:
                    data_connections.append(Connection(SELECTION.largest_connection_index + 1, direction, chosen_node,
                                                       60, direction.name))
                    SELECTION.largest_connection_index += 1


# Main 'game-loop'.
def start_input_loop():
    pygame.init()
    pygame.font.init()
    size = [SCRN_W + int((SCRN_W * 0.1)), SCRN_H]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('TFPS Map Viewer')
    data_nodes = get_node_data()
    data_connections = get_connection_data(data_nodes, True, True)
    find_simple_connections(data_nodes, data_connections)

    done = False
    while not done:
        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()

        if ALLOW_MAP_ADJUSTMENT:  # Change to true to allow map adjustment
            speed = 1
            if mods & pygame.KMOD_LSHIFT:
                speed = 10
            if keys[pygame.K_LEFT]:
                MAP_OFFSET[0] -= speed
            if keys[pygame.K_RIGHT]:
                MAP_OFFSET[0] += speed
            if keys[pygame.K_UP]:
                MAP_OFFSET[1] += speed
            if keys[pygame.K_DOWN]:
                MAP_OFFSET[1] -= speed

            if keys[pygame.K_SPACE]:
                print("map offset: ({0}, {1})".format(MAP_OFFSET[0], MAP_OFFSET[1]))

        if keys[pygame.K_SPACE]:
            print_formatted_connections(data_connections)

        mouse_pos = pygame.mouse.get_pos()
        mouse_event = "outside window"
        if OPTN_W > mouse_pos[0] > 0 and SCRN_H > mouse_pos[1] > 0:
            mouse_event = "over options"
        elif OPTN_W < mouse_pos[0] < SCRN_W and SCRN_H > mouse_pos[1] > 0:
            mouse_event = "over map"

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    print("Scrolled Up")
                    continue
                elif event.button == 5:
                    print("Scrolled Down")
                    continue
            elif event.type == pygame.MOUSEBUTTONUP:
                if mouse_event == "over map":
                    mouse_event = "clicked map"
                else:
                    mouse_event = "clicked options"

        SELECTION.hover_mode = "none"
        if mouse_event == "over options" or mouse_event == "clicked options":
            for i in range(NUM_OPTN):
                if mouse_pos[1] < SCRN_H / NUM_OPTN * (i + 1):
                    MODES = get_options(SELECTION.section)
                    if i < len(MODES):
                        SELECTION.hover_mode = MODES[i]
                        break

        if mouse_event == "clicked options" and not SELECTION.hover_mode == "ModeInfo":  # Option clicked
            if SELECTION.section == "Menu" and not SELECTION.hover_mode == "none":
                SELECTION.section = SELECTION.hover_mode
                SELECTION.mode = "None"
            elif SELECTION.hover_mode == "Menu":
                SELECTION.section = "Menu"
            else:
                SELECTION.mode = SELECTION.hover_mode

        if mouse_event == "clicked map":  # Map clicked
            # Do map logic based on which mode is selected
            print("Clicked Map at: (x={0}, y={1})".format(mouse_pos[0], mouse_pos[1]))
            if SELECTION.mode == "Select":
                select_mode_click(data_nodes, mouse_pos)
            elif SELECTION.mode == "Direction":
                direction_mode_click(mouse_pos)
            elif SELECTION.mode == "Target":
                target_mode_click(screen, data_nodes, data_connections, mouse_pos)
            elif SELECTION.mode == "Start Point" or SELECTION.mode == "Destination":
                choose_point_click(data_nodes, mouse_pos)
            elif SELECTION.mode == "Start Time":
                time_mode_click(data_nodes, data_connections, mouse_pos)

        if SELECTION.mode == "Select":
            draw_common(screen, data_nodes, data_connections)
            draw_in_select_mode(screen, data_nodes, mouse_pos, False)
        elif SELECTION.mode == "Direction":
            draw_common(screen, data_nodes, data_connections, draw_directions=False, draw_conns=False)
            draw_in_direction_mode(screen, data_nodes, mouse_pos)
        elif SELECTION.mode == "Target":
            draw_common(screen, data_nodes, data_connections, draw_conns=False)
            draw_in_target_mode(screen, data_nodes, mouse_pos)
        elif SELECTION.mode == "Start Point" or SELECTION.mode == "Direction":
            draw_common(screen, data_nodes, data_connections, draw_conns=False)
            draw_in_choose_point_mode(screen, data_nodes, mouse_pos, (mouse_event == "over map"))
        elif SELECTION.mode == "Start Time":
            draw_common(screen, data_nodes, data_connections, draw_scats=False, draw_conns=False)
            draw_in_time_mode(screen, mouse_pos)
        elif SELECTION.mode == "Results":
            draw_common(screen, data_nodes, data_connections, draw_scats=False, draw_conns=False)
            draw_path(screen)
        else:  # Draw in Info mode as default.
            draw_common(screen, data_nodes, data_connections)
            draw_in_info_mode(screen, data_nodes, mouse_pos, (mouse_event == "over map"))


start_input_loop()
