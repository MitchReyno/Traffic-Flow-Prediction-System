import pygame
import math
import pandas as pd


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (250, 250, 250)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 125, 0)
YELLOW = (255, 255, 0)
BROWN = (90, 65, 50)


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
        if dir_as_int == 1:
            return {0, 1}
        elif dir_as_int == 2:
            return {1, 1}
        elif dir_as_int == 3:
            return {1, 0}
        elif dir_as_int == 4:
            return {1, -1}
        elif dir_as_int == 5:
            return {0, -1}
        elif dir_as_int == 6:
            return {-1, -1}
        elif dir_as_int == 7:
            return {-1, 0}
        elif dir_as_int == 8:
            return {-1, 1}

    @staticmethod
    def pos_to_screen(pos, screen_width=1300, screen_height=700):
        min_lat = -37.8676
        max_lat = -37.78093
        min_long = 145.0083
        max_long = 145.09885
        lat_space = max_lat - min_lat
        long_space = max_long - min_long
        screen_x = ((pos[0] - min_lat) / lat_space) * screen_width
        screen_y = ((pos[1] - min_long) / long_space) * screen_height
        screen_pos = [int(screen_x), int(screen_y)]
        return screen_pos


class DirNode:
    def __init__(self, name, pos, dir):
        self.name = name
        self.pos = pos
        self.dir = dir


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


def start_map_creator_loop():
    done = False


def format_nodes(data):
    node_list = []
    last_scat = -1
    scat_node = SCATNode(-1)
    for row in data:
        pos = [row[3], row[4]]
        dir_node = DirNode(row[2], pos, row[5])
        if row[1] != last_scat:
            if last_scat != -1:
                scat_node.calculate_pos()
                node_list.append(scat_node)
            scat_node = SCATNode(row[1])
            last_scat = row[1]
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


def get_node_data(print_raw, print_formatted):
    pygame.init()
    pygame.font.init()

    # Get nodes from excel sheet
    data = "data/ScatsNodeData.xls"
    panda_nodes = pd.read_excel(data, sheet_name='Data', skiprows=1, nrows=140)
    nodes = pd.DataFrame(panda_nodes)

    if print_raw:
        for row in nodes.itertuples():
            print("[{0}] Scat {1}: {2}, coords({3}, {4}), dir = {5}".format(row[0], row[1], row[2], row[3], row[4],
                                                                            CardinalDir.int_to_short_str(row[5])))

    formatted_nodes = format_nodes(nodes.itertuples())
    if print_formatted:
        print_formatted_nodes(formatted_nodes)

    return formatted_nodes


def draw_common(screen, nodes):
    screen.fill(WHITE)
    node_rep_size = 5
    for node in nodes:
        print(CardinalDir.pos_to_screen(node.avg_pos))
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        pygame.draw.circle(screen, GREEN, screen_pos, node_rep_size, 1)
    pygame.display.flip()


def draw_in_info_mode(screen, nodes, mouse_pos):
    draw_common(screen, nodes)


def draw_in_select_mode():
    fake = False


def draw_in_direction_mode():
    fake = False


def draw_in_target_mode():
    fake = False


def draw_in_speed_mode():
    fake = False


def start_input_loop():
    size = [1300, 700]
    screen = pygame.display.set_mode(size)
    nodes = get_node_data(False, True)
    draw_in_info_mode(screen, nodes, [0, 0])

    mode = "info"
    done = False
    while not done:
        mouse_event = 0
        mouse_pos = {-1, -1}
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < 260:
                    mouse_event = 1
                else:
                    mouse_event = 2

        if mouse_event == 1:  # Option clicked
            if mouse_pos[1] < 100:
                # Info mode - safe mode just for 'viewing'
                mode = "info"
            elif mouse_pos[1] < 200:
                # Select mode - choose nodes, auto changes to 'direction'
                mode = "select"
            elif mouse_pos[1] < 300:
                # Direction mode - choose direction (N,S,E,W), auto changes to 'target'
                mode = "direction"
            elif mouse_pos[1] < 400:
                # Target mode - choose the SCAT which this node connects to.
                # Automatically connects to nearest direction, auto changes to 'speed'
                mode = "target"
            elif mouse_pos[1] < 500:
                # Speed mode - choose the speed of the road, auto changes to 'select'
                mode = "speed"
            print(mode)

        if mouse_event == 2:  # Map clicked
            print("Clicked Map at: (x={0}, y={1})".format(mouse_pos[0], mouse_pos[1]))



start_input_loop()
