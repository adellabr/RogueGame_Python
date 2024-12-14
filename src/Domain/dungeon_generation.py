import random
from enum import Enum


class Color(Enum):
    Green = 1,
    Red = 2,
    Blue = 3

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Constants:
    MAP_HEIGHT = 30
    MAP_WIDTH = 90
    ROOMS_PER_SIDE = 3
    MAX_ROOMS_NUMBER = ROOMS_PER_SIDE * ROOMS_PER_SIDE
    SECTOR_HEIGHT = MAP_HEIGHT // ROOMS_PER_SIDE
    SECTOR_WIDTH = MAP_WIDTH // ROOMS_PER_SIDE
    MIN_ROOM_HEIGHT = 3
    MIN_ROOM_WIDTH = 3
    MAX_ROOM_HEIGHT = MAP_HEIGHT // 3 - 4
    MAX_ROOM_WIDTH = MAP_WIDTH // 3 - 4
    MAX_TOP_COORDINATE = (SECTOR_HEIGHT - 6) // 2
    MAX_LEFT_COORDINATE = (SECTOR_WIDTH - 6) // 2
    VIEW_DISTANCE = 5

class Door:
    def __init__(self,position: Position):
        self.position = position
        self.color = random.choice(list(Color))
        self.is_open = False

class Room:
    def __init__(self, sector, position):
        self.sector = sector
        self.position = position
        self.number = sector * Constants.ROOMS_PER_SIDE + position
        self.top_coordinate = random.randint(1, Constants.MAX_TOP_COORDINATE + 1) + self.sector * Constants.SECTOR_HEIGHT
        self.left_coordinate = random.randint(1, Constants.MAX_LEFT_COORDINATE + 1) + self.position * Constants.SECTOR_WIDTH
        self.height = random.randint(Constants.MIN_ROOM_HEIGHT, Constants.MAX_ROOM_HEIGHT + self.sector * Constants.SECTOR_HEIGHT - self.top_coordinate)
        self.width = random.randint(Constants.MIN_ROOM_WIDTH, Constants.MAX_ROOM_WIDTH + self.position * Constants.SECTOR_WIDTH - self.left_coordinate)
        self.bot_coordinate = self.top_coordinate + self.height + 1
        self.right_coordinate = self.left_coordinate + self.width + 1
        self.connections = {"top": None, "right": None, "bottom": None, "left": None}
        self.doors = {"top": {'x': None, 'y': None},
                      "right": {'x': None, 'y': None},
                      "bottom": {'x': None, 'y': None},
                      "left": {'x': None, 'y': None}}

    def append_doors(self):
        if self.connections["top"] is not None:
            self.doors["top"]['y'] = self.top_coordinate
            self.doors["top"]['x'] = random.randint(self.left_coordinate + 1, self.right_coordinate - 1)
        if self.connections["right"] is not None:
            self.doors["right"]['x'] = self.right_coordinate
            self.doors["right"]['y'] = random.randint(self.top_coordinate + 1, self.bot_coordinate - 1)
        if self.connections["bottom"] is not None:
            self.doors["bottom"]['y'] = self.bot_coordinate
            self.doors["bottom"]['x'] = random.randint(self.left_coordinate + 1, self.right_coordinate - 1)
        if self.connections["left"] is not None:
            self.doors["left"]['x'] = self.left_coordinate
            self.doors["left"]['y'] = random.randint(self.top_coordinate + 1, self.bot_coordinate - 1)


class Corridor:
    def __init__(self):
        self.start_door = None
        self.finish_door = None
        self.points = []

    def generate_left_to_right_corridor(self, left_room, right_room):
        self.start_door = left_room.doors["right"].copy()
        self.finish_door = right_room.doors["left"].copy()
        start_point = left_room.doors["right"]
        finish_point = right_room.doors["left"]
        start_point['x'] += 1
        finish_point['x'] -= 1
        self.points.append(start_point)
        if finish_point['y'] != start_point['y'] and finish_point['x'] - start_point['x'] > 1:
            curve_x = random.randint(start_point['x'] + 1, finish_point['x'] - 1)
            curve1 = {'x': curve_x, 'y': start_point['y']}
            curve2 = {'x': curve_x, 'y': finish_point['y']}
            self.points.append(curve1)
            self.points.append(curve2)
        self.points.append(finish_point)

    def generate_top_to_bottom_corridor(self, up_room, down_room):
        self.start_door = up_room.doors["bottom"].copy()
        self.finish_door = down_room.doors["top"].copy()
        start_point = up_room.doors["bottom"]
        finish_point = down_room.doors["top"]
        start_point['y'] += 1
        finish_point['y'] -= 1
        self.points.append(start_point)
        if finish_point['x'] != start_point['x'] and finish_point['y'] - start_point['y'] > 1:
            curve_y = random.randint(start_point['y'] + 1, finish_point['y'] - 1)
            curve1 = {'x': start_point['x'], 'y': curve_y}
            curve2 = {'x': finish_point['x'], 'y': curve_y}
            self.points.append(curve1)
            self.points.append(curve2)
        self.points.append(finish_point)

    def generate_bottom_to_right_corridor(self, up_room, left_room):
        self.start_door = up_room.doors["bottom"].copy()
        self.finish_door = left_room.doors["right"].copy()
        start_point = up_room.doors["bottom"]
        finish_point = left_room.doors["right"]
        start_point['y'] += 1
        finish_point['x'] += 1
        self.points.append(start_point)
        curve = {'x': start_point['x'], 'y': finish_point['y']}
        self.points.append(curve)
        self.points.append(finish_point)

    def generate_bottom_to_left_corridor(self, up_room, right_room):
        self.start_door = up_room.doors["bottom"].copy()
        self.finish_door = right_room.doors["left"].copy()
        start_point = up_room.doors["bottom"]
        finish_point = right_room.doors["left"]
        start_point['y'] += 1
        finish_point['x'] -= 1
        self.points.append(start_point)
        curve = {'x': start_point['x'], 'y': finish_point['y']}
        self.points.append(curve)
        self.points.append(finish_point)

class Dungeon:
    def __init__(self):
        self.rooms = []
        self.rooms_2D = [[None for _ in range(Constants.ROOMS_PER_SIDE + 2)] for _ in
                         range(Constants.ROOMS_PER_SIDE + 2)]
        self.corridors = []
        self.create_rooms()
        self.generate_primary_connections()
        self.generate_secondary_connections()
        self.generate_doors()
        self.generate_corridors()

    def create_rooms(self):
        for sector in range(Constants.ROOMS_PER_SIDE):
            for position in range(Constants.ROOMS_PER_SIDE):
                # if sector == 1 and position == 2 or sector == 2 and position == 0 or sector == 2 and position == 1:
                if len(self.rooms) < 2 or random.random() < 0.5:
                    self.rooms.append(Room(sector, position))
                    self.rooms_2D[sector + 1][position + 1] = self.rooms[-1]

    def generate_primary_connections(self):
        for i in range(1, Constants.ROOMS_PER_SIDE + 1):
            for j in range(1, Constants.ROOMS_PER_SIDE + 1):
                if self.rooms_2D[i][j] is not None:
                    if self.rooms_2D[i - 1][j] is not None:
                        self.rooms_2D[i][j].connections["top"] = self.rooms_2D[i - 1][j].number
                    if self.rooms_2D[i][j + 1] is not None:
                        self.rooms_2D[i][j].connections["right"] = self.rooms_2D[i][j + 1].number
                    if self.rooms_2D[i + 1][j] is not None:
                        self.rooms_2D[i][j].connections["bottom"] = self.rooms_2D[i + 1][j].number
                    if self.rooms_2D[i][j - 1] is not None:
                        self.rooms_2D[i][j].connections["left"] = self.rooms_2D[i][j - 1].number

    def generate_bottom_connections(self, i):
        if self.rooms[i].position > self.rooms[i + 1].position:
            if i < len(self.rooms) - 2 and self.rooms[i + 2].sector == self.rooms[i + 1].sector:
                if self.rooms[i + 2].position > self.rooms[i].position:
                    self.rooms[i].connections["bottom"] = self.rooms[i + 2].number
                    self.rooms[i + 2].connections["top"] = self.rooms[i].number
                elif self.rooms[i + 2].position < self.rooms[i].position:
                    self.rooms[i].connections["bottom"] = self.rooms[i + 2].number
                    self.rooms[i + 2].connections["right"] = self.rooms[i].number
            elif self.rooms[i + 1].connections["right"] == None:
                self.rooms[i].connections["bottom"] = self.rooms[i + 1].number
                self.rooms[i + 1].connections["right"] = self.rooms[i].number
        elif self.rooms[i].position < self.rooms[i + 1].position and self.rooms[i + 1].connections["left"] == None:
            self.rooms[i].connections["bottom"] = self.rooms[i + 1].number
            self.rooms[i + 1].connections["left"] = self.rooms[i].number

    def generate_secondary_connections(self):
        for i in range(len(self.rooms) - 1):
            if self.rooms[i].sector == self.rooms[i + 1].sector and self.rooms[i].connections["right"] == None:
                self.rooms[i].connections["right"] = self.rooms[i + 1].number
                self.rooms[i + 1].connections["left"] = self.rooms[i].number
            elif self.rooms[i + 1].sector - self.rooms[i].sector == 1 and self.rooms[i].connections["bottom"] == None:
                self.generate_bottom_connections(i)
            elif self.rooms[i + 1].sector - self.rooms[i].sector == 2 and self.rooms[i].connections["bottom"] == None:
                self.rooms[i].connections["bottom"] = self.rooms[i + 1].number
                self.rooms[i + 1].connections["top"] = self.rooms[i].number

    def generate_doors(self):
        for room in self.rooms:
            room.append_doors()

    def generate_vertical_corridors(self, count):
        for i in range(1, Constants.ROOMS_PER_SIDE + 1):
            for j in range(1, Constants.ROOMS_PER_SIDE + 1):
                if self.rooms_2D[i][j] and self.rooms_2D[i + 1][j] and self.rooms_2D[i][j].connections["bottom"]:
                    if self.rooms_2D[i + 1][j].connections["top"] == self.rooms_2D[i][j].number:
                        self.corridors.append(Corridor())
                        self.corridors[count].generate_top_to_bottom_corridor(self.rooms_2D[i][j],
                                                                              self.rooms_2D[i + 1][j])
                        count += 1

    def generate_corridors(self):
        count = 0
        for i in range(len(self.rooms) - 1):
            if self.rooms[i].connections["right"] == self.rooms[i + 1].number:
                self.corridors.append(Corridor())
                self.corridors[count].generate_left_to_right_corridor(self.rooms[i], self.rooms[i + 1])
                count += 1
            if self.rooms[i].connections["bottom"] == self.rooms[i + 1].number:
                if self.rooms[i + 1].connections["right"] == self.rooms[i].number:
                    self.corridors.append(Corridor())
                    self.corridors[count].generate_bottom_to_right_corridor(self.rooms[i], self.rooms[i + 1])
                    count += 1
                elif self.rooms[i + 1].connections["left"] == self.rooms[i].number:
                    self.corridors.append(Corridor())
                    self.corridors[count].generate_bottom_to_left_corridor(self.rooms[i], self.rooms[i + 1])
                    count += 1
                elif self.rooms[i].sector - self.rooms[i + 1].sector == -2 and self.rooms[i + 1].connections["top"] == \
                        self.rooms[i].number:
                    self.corridors.append(Corridor())
                    self.corridors[count].generate_top_to_bottom_corridor(self.rooms[i], self.rooms[i + 1])
                    count += 1
            elif i < len(self.rooms) - 2 and self.rooms[i + 2].sector == self.rooms[i + 1].sector and \
                    self.rooms[i].connections["bottom"] == self.rooms[i + 2].number:
                if self.rooms[i + 2].connections["right"] == self.rooms[i].number:
                    self.corridors.append(Corridor())
                    self.corridors[count].generate_bottom_to_right_corridor(self.rooms[i], self.rooms[i + 2])
                    count += 1
                elif self.rooms[i + 2].position > self.rooms[i].position and self.rooms[i + 2].connections["top"] == \
                        self.rooms[i].number:
                    self.corridors.append(Corridor())
                    self.corridors[count].generate_top_to_bottom_corridor(self.rooms[i], self.rooms[i + 2])
                    count += 1
        self.generate_vertical_corridors(count)


class Map_dungeon:
    def __init__(self,dungeon:Dungeon):
        self.playground = [[' ' for j in range(Constants.MAP_WIDTH)] for i in range(Constants.MAP_HEIGHT)]
        self.dungeon = dungeon
        self.add_dungeon(dungeon)


    def add_room(self, room):
        for i in range(Constants.MAP_HEIGHT):
            for j in range(Constants.MAP_WIDTH):
                if i == room.top_coordinate:
                    if room.doors["top"] and room.doors["top"]['x'] == j:
                        self.playground[i][j] = '+'
                    elif j >= room.left_coordinate and j <= room.right_coordinate:
                        self.playground[i][j] = '-'
                elif i == room.bot_coordinate:
                    if room.doors["bottom"] and room.doors["bottom"]['x'] == j:
                        self.playground[i][j] = '+'
                    elif j >= room.left_coordinate and j <= room.right_coordinate:
                        self.playground[i][j] = '-'
                elif j == room.left_coordinate:
                    if room.doors["left"] and room.doors["left"]['y'] == i:
                        self.playground[i][j] = '+'
                    elif i > room.top_coordinate and i < room.bot_coordinate:
                        self.playground[i][j] = '|'
                elif j == room.right_coordinate:
                    if room.doors["right"] and room.doors["right"]['y'] == i:
                        self.playground[i][j] = '+'
                    elif i > room.top_coordinate and i < room.bot_coordinate:
                        self.playground[i][j] = '|'
                elif i > room.top_coordinate and i < room.bot_coordinate and j > room.left_coordinate and j < room.right_coordinate:
                    self.playground[i][j] = '.'

    def add_corridor(self, corridor):
        for i in range(len(corridor.points) - 1):
            if corridor.points[i]['x'] == corridor.points[i + 1]['x']:
                if corridor.points[i]['y'] < corridor.points[i + 1]['y']:
                    for j in range(corridor.points[i]['y'], corridor.points[i + 1]['y'] + 1):
                        self.playground[j][corridor.points[i]['x']] = '#'
                else:
                    for j in range(corridor.points[i + 1]['y'], corridor.points[i]['y'] + 1):
                        self.playground[j][corridor.points[i]['x']] = '#'
            elif corridor.points[i]['y'] == corridor.points[i + 1]['y']:
                if corridor.points[i]['x'] < corridor.points[i + 1]['x']:
                    for j in range(corridor.points[i]['x'], corridor.points[i + 1]['x'] + 1):
                        self.playground[corridor.points[i]['y']][j] = '#'
                else:
                    for j in range(corridor.points[i + 1]['x'], corridor.points[i]['x'] + 1):
                        self.playground[corridor.points[i]['y']][j] = '#'

    def add_dungeon(self, dungeon):
        for room in dungeon.rooms:
            self.add_room(room)
        for corridor in dungeon.corridors:
            self.add_corridor(corridor)

    def print_map(self):
        for i in range(Constants.MAP_HEIGHT):
            for j in range(Constants.MAP_WIDTH):
                print(self.playground[i][j], end='')
            print()


def create_map():
    map_dungeon = Map_dungeon(Dungeon())
    map_dungeon.print_map()

    return map_dungeon


if __name__ == "__main__":
    create_map()
