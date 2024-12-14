from enum import Enum
from random import randint, choice
from ..Domain import dungeon_generation


class Type_Monster(Enum):
    ZOMBIE = 1
    GHOST = 2
    OGRE = 3
    VAMPIRE = 4
    SNAKE_MAGICIAN = 5
    MIMIC = 6


class Type_Characteristic(Enum):
    HEALTH = 1
    POWER = 2
    DEXTERITY = 3


class Type_Object(Enum):
    TREASURE = 1
    MEAL = 2
    ELIXIR = 3
    SCROLL = 4
    WEAPON = 5


class Direction(Enum):
    Left = 1
    Right = 2
    Down = 3
    Up = 4


class Settings:
    MAX_HEALTH = 100
    LOW_CHARACTERISTIC = 40
    MIDDLE_CHARACTERISTIC = 60
    HIGH_CHARACTERISTIC = 80
    VERY_HIGH_CHARACTERISTIC = 100
    DEFAULT_HIT_CHANCE = 50
    HEIGHT = 30  # высота
    WIDTH = 90  # ширина
    LIST_DIRECTION = [Direction.Left, Direction.Right, Direction.Up, Direction.Down]
    DIRECTION_MAP = {
        Direction.Left: (-1, 0),
        Direction.Right: (1, 0),
        Direction.Up: (0, -1),
        Direction.Down: (0, 1),
    }
    DIRECTION_SNAKE = {
        Direction.Left: (-1, -1),
        Direction.Right: (1, 1),
        Direction.Up: (1, -1),
        Direction.Down: (-1, 1),
    }
    LEVEL_ITEMS = {1: 1}
    LEVEL_ITEMS.update({i: 2 for i in range(2, 10)})
    LEVEL_ITEMS.update({i: 3 for i in range(10, 15)})
    LEVEL_ITEMS.update({i: 4 for i in range(15, 22)})


class Size_object(Enum):
    SMALL = 5
    MIDDLE = 7
    BIG = 10
    VERY_BIG = 15


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Monster:
    def __init__(
        self,
        type_monster: Type_Monster,
        position: Position,
    ):
        self.type = type_monster
        self.dexterity, self.power, self.hostility, self.health = self.set_parameters()
        self.position = position
        self.direction = choice(Settings.LIST_DIRECTION)
        self.strike_number = 0
        self.mask = True

    def moving(self, playground: list):
        position_before_moving = Position(self.position.x, self.position.y)
        dx, dy = Settings.DIRECTION_MAP.get(self.direction, (0, 0))
        if self.type == Type_Monster.OGRE:
            dx *= 2
            dy *= 2
            if playground[self.position.y + dy][self.position.x + dx] != ".":
                dx //= 2
                dy //= 2
        elif self.type == Type_Monster.SNAKE_MAGICIAN:
            dx, dy = Settings.DIRECTION_SNAKE.get(self.direction, (0, 0))
        self.position.x += dx
        self.position.y += dy
        if playground[self.position.y][self.position.x] != ".":
            self.position = position_before_moving
            self.direction = choice(Settings.LIST_DIRECTION)
            self.moving(playground)

    def direction_of_the_chase(self, user_position: Position):
        if self.position.y == user_position.y:
            self.direction = (
                Direction.Left if self.position.x > user_position.x else Direction.Right
            )
        elif self.position.x == user_position.x:
            self.direction = (
                Direction.Up if self.position.y > user_position.y else Direction.Down
            )
        else:
            list_dir = [
                Direction.Up if self.position.y > user_position.y else Direction.Down,
                (
                    Direction.Left
                    if self.position.x > user_position.x
                    else Direction.Right
                ),
            ]
            self.direction = choice(list_dir)

    def set_parameters(self):
        if self.type == Type_Monster.ZOMBIE:
            return (
                Settings.LOW_CHARACTERISTIC,
                Settings.MIDDLE_CHARACTERISTIC,
                Settings.MIDDLE_CHARACTERISTIC,
                Settings.HIGH_CHARACTERISTIC,
            )
        elif self.type == Type_Monster.VAMPIRE:
            return (
                Settings.HIGH_CHARACTERISTIC,
                Settings.MIDDLE_CHARACTERISTIC,
                Settings.HIGH_CHARACTERISTIC,
                Settings.HIGH_CHARACTERISTIC,
            )
        elif self.type == Type_Monster.GHOST:
            return (
                Settings.HIGH_CHARACTERISTIC,
                Settings.LOW_CHARACTERISTIC,
                Settings.LOW_CHARACTERISTIC,
                Settings.LOW_CHARACTERISTIC,
            )
        elif self.type == Type_Monster.OGRE:
            return (
                Settings.LOW_CHARACTERISTIC,
                Settings.VERY_HIGH_CHARACTERISTIC,
                Settings.MIDDLE_CHARACTERISTIC,
                Settings.VERY_HIGH_CHARACTERISTIC,
            )
        elif self.type == Type_Monster.SNAKE_MAGICIAN:
            return (
                Settings.VERY_HIGH_CHARACTERISTIC,
                Settings.HIGH_CHARACTERISTIC,
                Settings.MIDDLE_CHARACTERISTIC,
                Settings.VERY_HIGH_CHARACTERISTIC,
            )
        elif self.type == Type_Monster.MIMIC:
            return (
                Settings.HIGH_CHARACTERISTIC,
                Settings.LOW_CHARACTERISTIC,
                Settings.LOW_CHARACTERISTIC,
                Settings.HIGH_CHARACTERISTIC,
            )


class Object:
    def __init__(
        self,
        type_object: Type_Object,
        size_object: Size_object,
        position: Position,
        characteristic: Type_Characteristic = None,
    ):
        self.type_object = type_object
        self.size_object = size_object
        self.characteristic = characteristic
        self.position = position
        self.duration = (
            self.size_object.value * 2 if self.type_object == Type_Object.ELIXIR else 0
        )

    def add_meal_or_elixir_or_scroll(self):
        add_characteristics = self.size_object.value
        if (
            self.type_object == Type_Object.ELIXIR
            or self.type_object == Type_Object.MEAL
        ):
            add_characteristics *= 2
        return int(add_characteristics)


class Backpack:
    def __init__(self):
        self.max_size = 9
        self.meal_list = list()
        self.elixir_list = list()
        self.scroll_list = list()
        self.weapon_list = list()
        self.temporary_effect_list = list()
        self.throw_away_weapon = None
        self.object_dict = {
            Type_Object.MEAL: self.meal_list,
            Type_Object.ELIXIR: self.elixir_list,
            Type_Object.SCROLL: self.scroll_list,
            Type_Object.WEAPON: self.weapon_list,
        }

    def add_object(self, new_object: Object):
        result = False
        if (
            new_object.type_object in self.object_dict
            and len(self.object_dict[new_object.type_object]) <= self.max_size
        ):
            self.object_dict[new_object.type_object].append(new_object)
            result = True
        return result

    def delite_object(self, del_object: Object):
        if (
            del_object.type_object in self.object_dict
            and self.check_object_in_backpack(del_object)
        ):
            self.object_dict[del_object.type_object].remove(del_object)
        if del_object.type_object == Type_Object.ELIXIR:
            self.temporary_effect_list.append(del_object)

    def check_object_in_backpack(self, check_object: Object):
        return check_object in self.object_dict[check_object.type_object]


class Character:
    def __init__(self, position: Position):
        self.max_health = Settings.MAX_HEALTH
        self.health = Settings.MIDDLE_CHARACTERISTIC
        self.dexterity = Settings.MIDDLE_CHARACTERISTIC
        self.power = Settings.MIDDLE_CHARACTERISTIC
        self.backpack = Backpack()
        self.position = position
        self.direction = Direction.Right
        self.stands_symbol = "."
        self.score = 0
        self.weapon = None
        self.food_amount = 0
        self.elixir_amount = 0
        self.scroll_amount = 0
        self.cells_amount = 0
        self.killed_enemies_amount = 0
        self.hits_amount = 0
        self.missed_hits_amount = 0

    def moving(self, playground: list):
        self.check_temporary_effect()
        position_before_moving = Position(self.position.x, self.position.y)
        dx, dy = Settings.DIRECTION_MAP.get(self.direction, (0, 0))
        self.position.x += dx
        self.position.y += dy
        if (
            playground[self.position.y][self.position.x]
            not in ".+#mMlLcСfFtTyYeErRwWqQX"
        ):
            self.position = position_before_moving
        is_attacking = (
            playground[self.position.y][self.position.x] in "mMlLcСfFtTyYeErRwWqQ"
        )
        self.stands_symbol = playground[self.position.y][self.position.x]
        return is_attacking

    def acquire_object(self, obj: Object):
        if obj.type_object != Type_Object.TREASURE:
            self.backpack.add_object(obj)
        else:
            self.score += obj.size_object.value * 10

    def open_backpack(self, type_object: Type_Object, number_object):
        number_object = int(number_object - ord("0"))
        if not 1 <= number_object <= 9:
            return
        if (
            type_object == Type_Object.ELIXIR
            and len(self.backpack.elixir_list) >= number_object
        ):
            self.use_object(self.backpack.elixir_list[number_object - 1])
        elif (
            type_object == Type_Object.MEAL
            and len(self.backpack.meal_list) >= number_object
        ):
            self.use_object(self.backpack.meal_list[number_object - 1])
        elif (
            type_object == Type_Object.SCROLL
            and len(self.backpack.scroll_list) >= number_object
        ):
            self.use_object(self.backpack.scroll_list[number_object - 1])
        elif (
            type_object == Type_Object.WEAPON
            and len(self.backpack.weapon_list) >= number_object
        ):
            self.use_object(self.backpack.weapon_list[number_object - 1])

    def use_object(self, obj: Object):
        if self.backpack.check_object_in_backpack(obj):
            self.apply_object_effect(obj)
            self.backpack.delite_object(obj)
        else:
            self.health = 100

    def apply_object_effect(self, obj: Object, del_eff=False):
        sign = 1
        if del_eff:
            sign = -1
        if obj.type_object == Type_Object.MEAL:
            self.health = min(
                self.health + obj.add_meal_or_elixir_or_scroll(),
                self.max_health,
            )
            self.food_amount += 1
        elif (
            obj.type_object == Type_Object.ELIXIR
            or obj.type_object == Type_Object.SCROLL
        ):
            add_characteristics = sign * obj.add_meal_or_elixir_or_scroll()
            self.max_health += (
                add_characteristics
                if obj.characteristic == Type_Characteristic.HEALTH
                else 0
            )
            self.power += (
                add_characteristics
                if obj.characteristic == Type_Characteristic.POWER
                else 0
            )
            self.dexterity += (
                add_characteristics
                if obj.characteristic == Type_Characteristic.DEXTERITY
                else 0
            )
            if obj.type_object == Type_Object.ELIXIR:
                self.elixir_amount += 1
            else:
                self.scroll_amount += 1
        elif obj.type_object == Type_Object.WEAPON:
            add_characteristics = obj.size_object.value
            self.power += add_characteristics
            if self.weapon is not None:
                self.power -= self.weapon.size_object.value
                self.backpack.throw_away_weapon = self.weapon
            self.weapon = obj

    def check_temporary_effect(self):
        for elixir in self.backpack.temporary_effect_list:
            elixir.duration = elixir.duration - 1
            if elixir.duration <= 0:
                self.apply_object_effect(elixir, True)
                self.backpack.temporary_effect_list.remove(elixir)

    def blow_simulation(self, monster: Monster):
        damage = blow_simulation(self.dexterity, self.power, monster.dexterity)
        monster.health -= damage

    def power_simulation(self, monster: Monster):
        damage = blow_simulation(monster.dexterity, monster.power, self.dexterity)
        if monster.type == Type_Monster.VAMPIRE and monster.strike_number == 0:
            monster.strike_number = 1
            damage = 0
        self.health -= damage
        self.hits_amount += 1
        if damage == 0:
            self.missed_hits_amount += 1


def blow_simulation(dexterity_attack: int, power_attack: int, dexterity_protect: int):
    hit_chance = Settings.DEFAULT_HIT_CHANCE + dexterity_attack - dexterity_protect
    res_hit = False
    if hit_chance >= 100:
        res_hit = True
    elif hit_chance > 0:
        res_hit = randint(0, 100) < hit_chance
    damage = 0
    if res_hit:
        damage = randint(
            power_attack // 2 - power_attack // 3, power_attack // 2 + power_attack // 3
        )
    return damage


class Exit:
    def __init__(self, last_room):
        self.position = self.define_position(last_room)

    def define_position(self, last_room):
        pos_x = randint(last_room.left_coordinate + 1, last_room.right_coordinate - 1)
        pos_y = randint(last_room.top_coordinate + 1, last_room.bot_coordinate - 1)
        return Position(pos_x, pos_y)


class Gameplay:
    def __init__(self, level: int):
        self.level = level
        self.map_dungeon = dungeon_generation.Map_dungeon(dungeon_generation.Dungeon())
        self.user = Character(
            Position(
                self.map_dungeon.dungeon.rooms[0].left_coordinate + 1,
                self.map_dungeon.dungeon.rooms[0].top_coordinate + 1,
            )
        )
        self.exit = Exit(self.map_dungeon.dungeon.rooms[-1])
        self.monster_list = list()
        self.object_list = list()
        self.add_monster_in_map()
        self.add_useful_items()
        self.visited_rooms = [self.map_dungeon.dungeon.rooms[0]]
        self.visited_corridors = []
        self.current_room = self.map_dungeon.dungeon.rooms[0]
        self.game_status = True
        self.critical_situation = 0
        self.easy_situation = 0

    def append_visited(self, pos_user_bef_move):
        if (
            self.map_dungeon.playground[self.user.position.y][self.user.position.x]
            == "#"
            and self.map_dungeon.playground[pos_user_bef_move.y][pos_user_bef_move.x]
            == "+"
        ):
            self.current_room = None
            if (
                self.map_dungeon.dungeon.rooms_2D[pos_user_bef_move.y // 10 + 1][
                    pos_user_bef_move.x // 30 + 1
                ]
                not in self.visited_rooms
            ):
                self.visited_rooms.append(
                    self.map_dungeon.dungeon.rooms_2D[pos_user_bef_move.y // 10 + 1][
                        pos_user_bef_move.x // 30 + 1
                    ]
                )
            for corridor in self.map_dungeon.dungeon.corridors:
                if (
                    corridor not in self.visited_corridors
                    and corridor.start_door
                    == {"x": pos_user_bef_move.x, "y": pos_user_bef_move.y}
                    or corridor.finish_door
                    == {"x": pos_user_bef_move.x, "y": pos_user_bef_move.y}
                ):
                    self.visited_corridors.append(corridor)
        elif (
            self.map_dungeon.playground[self.user.position.y][self.user.position.x]
            == "+"
            and self.map_dungeon.playground[pos_user_bef_move.y][pos_user_bef_move.x]
            == "#"
        ):
            self.current_room = self.map_dungeon.dungeon.rooms_2D[
                pos_user_bef_move.y // 10 + 1
            ][pos_user_bef_move.x // 30 + 1]

    def check_situation_in_game(self):
        if self.user.health <= 10 and len(self.user.backpack.meal_list) == 0:
            self.critical_situation += 1
            self.easy_situation = 0
        elif (
            self.user.health >= 90
            and self.user.power >= 75
            and self.user.dexterity >= 80
        ):
            self.easy_situation += 1
            self.critical_situation = 0
        if self.is_critical_condition_met():
            self.add_meal_in_critical_situation()
            self.weaken_monster_in_critical_situation()
        elif self.is_game_too_easy():
            self.weaken_monster_in_easy_situation()

    def is_critical_condition_met(self):
        return (
            self.critical_situation == 100
            or (self.level >= 5 and self.critical_situation == 200)
            or (self.level >= 20 and self.critical_situation == 350)
        )

    def is_game_too_easy(self):
        return (
            self.easy_situation == 200
            or (self.level >= 5 and self.easy_situation == 350)
            or (self.level >= 20 and self.easy_situation == 500)
        )

    def weaken_monster_in_easy_situation(self):
        for monster in self.monster_list:
            if monster.type.value < 3:
                position_monster = monster.position
                self.monster_list.remove(monster)
                self.monster_list.append(
                    Monster(Type_Monster.SNAKE_MAGICIAN, position_monster)
                )

    def weaken_monster_in_critical_situation(self):
        for monster in self.monster_list:
            if monster.type.value >= 3:
                position_monster = monster.position
                self.monster_list.remove(monster)
                self.monster_list.append(Monster(Type_Monster.ZOMBIE, position_monster))

    def add_meal_in_critical_situation(self):
        current_room = (
            self.current_room
            if self.current_room is not None
            else self.visited_rooms[0]
        )
        for number_room in current_room.connections.values():
            room = self.find_room(number_room)
            if room is not None:
                self.add_useful_items_in_room(room, Type_Object.MEAL)

    def find_room(self, number_room: int):
        if number_room is None:
            return None
        for room in self.map_dungeon.dungeon.rooms:
            if room.number == number_room:
                return room
        return None

    def pickup_object(self):
        for my_object in self.object_list:
            if my_object.position == self.user.position:
                self.user.acquire_object(my_object)
                self.object_list.remove(my_object)
                self.map_dungeon.playground[self.user.position.y][
                    self.user.position.x
                ] = "."
                break

    def is_position_in_current_room(self, position: Position):
        return (
            self.current_room.left_coordinate
            < position.x
            < self.current_room.right_coordinate
            and self.current_room.top_coordinate
            < position.y
            < self.current_room.bot_coordinate
        )

    def user_in_zone(self, monster_pos: Position, zone: int):
        return (
            self.current_room is not None
            and self.is_position_in_current_room(monster_pos)
            and (self.user.position.x >= monster_pos.x - zone)
            and (self.user.position.x <= monster_pos.x + zone)
            and (self.user.position.y >= monster_pos.y - zone)
            and (self.user.position.y <= monster_pos.y + zone)
        )

    def moving(self):
        position_user_before_move = Position(self.user.position.x, self.user.position.y)
        self.check_situation_in_game()
        if self.user.moving(self.map_dungeon.playground):
            self.pickup_object()
        for monster in self.monster_list:
            battle_flag = False
            if self.user.position == monster.position:
                self.user.position = position_user_before_move
                self.user.blow_simulation(monster)
                battle_flag = True
                if monster.health <= 0:
                    self.add_treasure_in_map(monster)
                    self.monster_list.remove(monster)
                    self.user.killed_enemies_amount += 1
                else:
                    self.user.power_simulation(monster)

            position_monster_before_move = Position(
                monster.position.x, monster.position.y
            )
            self.moving_monster(monster)
            if self.are_monster_at_same_position(monster):
                monster.position = position_monster_before_move
            if self.user.position == monster.position:
                monster.position = position_monster_before_move
                if not battle_flag:
                    self.user.power_simulation(monster)
                    if self.user.health > 0:
                        self.user.blow_simulation(monster)
                    if monster.health <= 0:
                        self.add_treasure_in_map(monster)
                        self.monster_list.remove(monster)
        self.throw_away_the_weapon()
        self.append_visited(position_user_before_move)

    def are_monster_at_same_position(self, monster: Monster):
        for m in self.monster_list:
            if m.type != monster.type and m.position == monster.position:
                return True
        return False

    def moving_monster(self, monster: Monster):
        zone_aggression = monster.hostility // 15
        monster_sees_the_user = self.user_in_zone(monster.position, zone_aggression)
        if monster_sees_the_user:
            monster.direction_of_the_chase(self.user.position)
        elif monster.type == Type_Monster.GHOST and randint(1, 2) == 1:
            room = self.room_ghost(monster)
            monster.position.x = randint(
                room.left_coordinate + 1, room.right_coordinate - 1
            )
            monster.position.y = randint(
                room.top_coordinate + 1, room.bot_coordinate - 1
            )
        elif randint(1, 3) == 3:
            monster.direction = choice(Settings.LIST_DIRECTION)
        if monster.type == Type_Monster.MIMIC and not monster_sees_the_user:
            monster.mask = True
        else:
            monster.mask = False
        if not monster.mask:
            monster.moving(self.map_dungeon.playground)

        return monster.position

    def room_ghost(self, monster: Monster):
        for room in self.map_dungeon.dungeon.rooms:
            if (
                room.left_coordinate <= monster.position.x <= room.right_coordinate
                and room.top_coordinate <= monster.position.y <= room.bot_coordinate
            ):
                return room
        return None

    def add_monster_in_map(self):
        flag = True
        for room in self.map_dungeon.dungeon.rooms:
            if flag:
                flag = False
                continue
            type_monster = self.type_monster()
            pos_x = randint(room.left_coordinate + 1, room.right_coordinate - 1)
            pos_y = randint(room.top_coordinate + 1, room.bot_coordinate - 1)
            self.monster_list.append(Monster(type_monster, Position(pos_x, pos_y)))
            if randint(1, 7) == 1:
                self.add_mimic(room)

    def add_mimic(self, room):
        flag = True
        while flag:
            pos_x = randint(room.left_coordinate + 1, room.right_coordinate - 1)
            pos_y = randint(room.top_coordinate + 1, room.bot_coordinate - 1)
            new_position = Position(pos_x, pos_y)
            for monster in self.monster_list:
                if monster.position == new_position:
                    flag = True
                    break
                flag = False
            if not flag:
                self.monster_list.append(Monster(Type_Monster.MIMIC, new_position))

    def type_monster(self):
        type_monster = choice(list(Type_Monster))
        if type_monster.value > self.level:
            type_monster = self.type_monster()
        return type_monster

    def add_treasure_in_map(self, monster: Monster):
        size_object = Size_object.VERY_BIG
        if monster.type == Type_Monster.ZOMBIE:
            size_object = Size_object.SMALL
        elif monster.type == Type_Monster.OGRE or monster.type == Type_Monster.GHOST:
            size_object = Size_object.MIDDLE
        elif monster.type == Type_Monster.VAMPIRE:
            size_object = Size_object.VERY_BIG
        self.object_list.append(
            Object(
                Type_Object.TREASURE,
                size_object,
                Position(monster.position.x, monster.position.y),
            )
        )

    def add_useful_items(self):
        for room in self.map_dungeon.dungeon.rooms:
            for _ in range(
                randint(
                    0,
                    Settings.LEVEL_ITEMS[self.level]
                    + ((room.height * room.width) // 20),
                )
            ):
                self.add_useful_items_in_room(room)

    def are_coordinates_different(self, new_position: Position):
        if self.exit.position == new_position:
            return False
        for obj in self.object_list:
            if obj.position == new_position:
                return True
        return False

    def create_new_position_items(self, room):
        numbers_iteration = 0
        while True:
            numbers_iteration += 1
            new_position = Position(
                randint(room.left_coordinate + 1, room.right_coordinate - 1),
                randint(room.top_coordinate + 1, room.bot_coordinate - 1),
            )
            if (
                not self.are_coordinates_different(new_position)
                or numbers_iteration == 20
            ):
                return new_position

    def add_useful_items_in_room(self, room, type_object: Type_Object = None):
        type_object = choice(list(Type_Object)) if type_object is None else type_object
        size_object = choice(list(Size_object))
        type_characteristic = choice(list(Type_Characteristic))
        new_position = self.create_new_position_items(room)
        self.object_list.append(
            Object(
                type_object,
                size_object,
                new_position,
                type_characteristic,
            )
        )

    def throw_away_the_weapon(self):
        weapon = self.user.backpack.throw_away_weapon
        if weapon is not None:
            pos_user_x = self.user.position.x
            pos_user_y = self.user.position.y
            directions = [
                (0, -1),
                (0, 1),
                (-1, 0),
                (1, 0),
                (1, 1),
                (-1, 1),
                (-1, -1),
                (1, -1),
            ]
            for dx, dy in directions:
                new_x = pos_user_x + dx
                new_y = pos_user_y + dy
                if self.map_dungeon.playground[new_y][new_x] in ".#":
                    pos_obj_x, pos_obj_y = new_x, new_y
                    break
            else:
                pos_obj_x, pos_obj_y = pos_user_x, pos_user_y

            weapon.position = Position(pos_obj_x, pos_obj_y)
            self.object_list.append(weapon)
            self.user.backpack.throw_away_weapon = None
