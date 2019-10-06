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

OPTN_W = 200
SCRN_H = 790
SCRN_W = int((0.82484 * SCRN_H)) + OPTN_W

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
    def ORIGINAL_pos_to_screen(pos, screen_width=SCRN_W, screen_height=SCRN_H, options_width=OPTN_W):
        offset_lat = -0.0016827
        offset_long = -0.0013543
        min_lat = -37.8676
        max_lat = -37.78093
        min_long = 145.0083
        max_long = 145.09885
        lat_offset = 0.000
        long_offset = 0.000
        lat_space = max_lat - min_lat
        long_space = max_long - min_long
        screen_x = ((pos[0] + lat_offset - min_lat) / lat_space) * (screen_width - options_width) + options_width
        screen_y = ((pos[1] + long_offset - min_long) / long_space) * screen_height
        screen_pos = [int(screen_x), int(screen_y)]
        return screen_pos

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


def draw_common(screen, nodes, map_img, map_offset):
    screen.fill(WHITE)
    screen.blit(map_img, (OPTN_W + map_offset[0], map_offset[1]))
    node_rep_size = 5
    for node in nodes:
        screen_pos = CardinalDir.pos_to_screen(node.avg_pos)
        pygame.draw.circle(screen, GREEN, screen_pos, node_rep_size, 1)
        for scat in node.directions:
            screen_pos = CardinalDir.pos_to_screen(scat.pos)
            pygame.draw.circle(screen, BLUE, screen_pos, node_rep_size, 1)


def draw_in_info_mode(screen, nodes, map_img, mouse_pos, map_offset):
    draw_common(screen, nodes, map_img, map_offset)
    closest = 1000
    chosen_scat = nodes[0]
    for node in nodes:
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


def draw_in_select_mode():
    fake = False


def draw_in_direction_mode():
    fake = False


def draw_in_target_mode():
    fake = False


def draw_in_speed_mode():
    fake = False


def start_input_loop():
    size = [SCRN_W  + int((SCRN_W * 0.1)), SCRN_H]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('TFPS Map Viewer')
    nodes = get_node_data(False, True)
    map_img = pygame.image.load("data/final_map.png")

    #draw_in_info_mode(screen, nodes, map_img, [0, 0])

    mode = "info"
    map_offset = [-154, 0]
    done = False
    while not done:
        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()

        if False:  # Change to true to allow map adjustment
            speed = 1
            if mods & pygame.KMOD_LSHIFT:
                speed = 10
            if keys[pygame.K_LEFT]:
                map_offset[0] -= speed
            if keys[pygame.K_RIGHT]:
                map_offset[0] += speed
            if keys[pygame.K_UP]:
                map_offset[1] += speed
            if keys[pygame.K_DOWN]:
                map_offset[1] -= speed

            if keys[pygame.K_SPACE]:
                print("map offset: ({0}, {1})".format(map_offset[0], map_offset[1]))

        mouse_event = 0
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONUP:
                if mouse_pos[0] < OPTN_W:
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

        draw_in_info_mode(screen, nodes, map_img, mouse_pos, map_offset)


start_input_loop()
