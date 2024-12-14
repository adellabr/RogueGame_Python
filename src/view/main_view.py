import curses
import os

from src.Business_Logic.model import Type_Object, Settings, Type_Monster
from ..Business_Logic import model
from ..Domain import dungeon_generation
from enum import Enum
from ..datalayer import statistic
import math


class Menu_Status(Enum):
    PLAY = 1
    CONTINUE = 3
    EXIT = 5


class Constant:
    HEIGHT = 40  # высота
    WIDTH = 90  # ширина
    HEALTH_BAR_X = 1
    HEALTH_BAR_Y = 31
    CHARACTERISTIC_VAL_X = HEALTH_BAR_X
    CHARACTERISTIC_VAL_Y = HEALTH_BAR_Y + 1
    BACKPACK_INF_X = 3
    BACKPACK_Y = 15
    BACK_CONTENT_X = HEALTH_BAR_X + 25
    BACK_CONTENT_Y = HEALTH_BAR_Y
    COLOR_LIST = [4, 1, 3, 5]
    OBJECT_VIEW = {
        model.Type_Object.MEAL: "mMlL",
        model.Type_Object.SCROLL: "cСfF",
        model.Type_Object.TREASURE: "tTyY",
        model.Type_Object.ELIXIR: "eErR",
        model.Type_Object.WEAPON: "wWqQ"
    }
    OBJECT_TYPE = {
        ord("e"): model.Type_Object.SCROLL,
        ord("k"): model.Type_Object.ELIXIR,
        ord("j"): model.Type_Object.MEAL,
        ord("h"): model.Type_Object.WEAPON
    }
    SIZE = {5: 0, 7: 1, 10: 2, 15: 3}


class Visible_map(dungeon_generation.Map_dungeon):
    def __init__(self, gameplay: model.Gameplay):
        self.gameplay = gameplay
        self.playground = [[' ' for j in range(dungeon_generation.Constants.MAP_WIDTH)] for i in
                           range(dungeon_generation.Constants.MAP_HEIGHT)]

    def cast_ray(self, angle):
        step_size = 1
        distance = 0
        while distance < dungeon_generation.Constants.VIEW_DISTANCE:
            distance += step_size
            ray_x = self.gameplay.user.position.x + int(math.cos(angle) * distance)
            ray_y = self.gameplay.user.position.y + int(math.sin(angle) * distance)
            if ray_x < 0 or ray_x >= dungeon_generation.Constants.MAP_WIDTH or ray_y < 0 or ray_y >= dungeon_generation.Constants.MAP_HEIGHT:
                break
            self.playground[ray_y][ray_x] = self.gameplay.map_dungeon.playground[ray_y][ray_x]
            if self.gameplay.map_dungeon.playground[ray_y][ray_x] in ('#', '-', '|', '+',):
                break

    def apply_fog_of_war(self, room):
        for angle in range(0, 360, 5):
            self.cast_ray(math.radians(angle))

    def update_current_room(self):
        for i in range(self.gameplay.current_room.top_coordinate + 1, self.gameplay.current_room.bot_coordinate):
            for j in range(self.gameplay.current_room.left_coordinate + 1, self.gameplay.current_room.right_coordinate):
                if self.playground[i][j] in ('P', 'V', 'G', 'O', 'Z', 'S'):
                    self.playground[i][j] = '.'

    def add_current_room(self, room):
        self.update_current_room()
        if room in self.gameplay.visited_rooms:
            for i in range(room.top_coordinate, room.bot_coordinate):
                for j in range(room.left_coordinate, room.right_coordinate):
                    self.playground[i][j] = self.gameplay.map_dungeon.playground[i][j]
        else:
            self.apply_fog_of_war(self.gameplay.current_room)

    def add_visited_rooms_corridors(self):
        for room in self.gameplay.visited_rooms:
            self.add_room(room)
        for corridor in self.gameplay.visited_corridors:
            self.add_corridor(corridor)
        self.add_monsters()
        self.add_objects()
        self.add_exit()
        if self.gameplay.current_room:
            self.add_current_room(self.gameplay.current_room)

    def add_objects(self):
        for my_object in self.gameplay.object_list:
            self.gameplay.map_dungeon.playground[my_object.position.y][my_object.position.x] \
                = Constant.OBJECT_VIEW[my_object.type_object][Constant.SIZE[my_object.size_object.value]]

    def add_exit(self):
        self.gameplay.map_dungeon.playground[self.gameplay.exit.position.y][self.gameplay.exit.position.x] = 'X'

    def add_monsters(self):
        monster_view = {
            model.Type_Monster.ZOMBIE: ["Z", 1],
            model.Type_Monster.VAMPIRE: ["V", 5],
            model.Type_Monster.GHOST: ["G", 4],
            model.Type_Monster.OGRE: ["O", 3],
            model.Type_Monster.SNAKE_MAGICIAN: ["S", 4],
            model.Type_Monster.MIMIC: ["J", 4],
        }
        for monster in self.gameplay.monster_list:
            if monster.type == Type_Monster.MIMIC and monster.mask:
                self.gameplay.map_dungeon.playground[monster.position.y][monster.position.x] \
                    = 'j'
            else:
                self.gameplay.map_dungeon.playground[monster.position.y][monster.position.x] \
                    = monster_view[monster.type][0]

    def delete_monster(self):
        for monster in self.gameplay.monster_list:
            self.gameplay.map_dungeon.playground[monster.position.y][monster.position.x] = '.'


def main(stdscr):
    screen = curses.newwin(
        dungeon_generation.Constants.MAP_HEIGHT + 10,
        dungeon_generation.Constants.MAP_WIDTH + 2,
        0,
        0,
    )
    stat_screen = init_statistic_screen()
    curses.curs_set(False)
    init_pair()
    while True:
        status = create_menu(screen)
        level = 1
        is_continue = False
        save_state = statistic.Save_state()
        if status == Menu_Status.PLAY.value:
            is_continue = False
            if os.path.exists('src/game_stats/level_statistics.json'):
                os.remove('src/game_stats/level_statistics.json')
            if os.path.exists("src/game_stats/game_state.json"):
                os.remove("src/game_stats/game_state.json")
            start_game(screen, stat_screen, level, is_continue, save_state)
        elif status == Menu_Status.CONTINUE.value:
            if save_state.import_state():
                level = save_state.import_dict["Level"]
                is_continue = True
                start_game(screen, stat_screen, level, is_continue, save_state)
        elif status == Menu_Status.EXIT.value:
            break
        
def start_game(screen, stat_screen, level, is_continue, save_state):
     user_helth = True
     while user_helth and level <= 21:
        gameplay = model.Gameplay(level)
        if is_continue:
            save_state.update_parameteres(gameplay)
        start_game_loop(screen,stat_screen, gameplay, is_continue)
        is_continue = False
        user_helth = gameplay.game_status
        if gameplay.game_status and gameplay.user.health > 0:
            level += 1


def init_pair():
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_RED, curses.COLOR_RED)


def create_menu(screen: curses.window):
    menu = {
        Menu_Status.PLAY: " Н о в а я  и г р а ",
        Menu_Status.CONTINUE: " П р о д о л ж и т ь ",
        Menu_Status.EXIT: "     В ы х о д     ",
    }
    number_menu = 1
    while True:
        screen.clear()
        screen.attron(curses.color_pair(2))
        screen.border()
        screen.attroff(curses.color_pair(2))
        screen.addstr(Constant.HEIGHT // 2 - 6, Constant.WIDTH // 2 - 3, "М Е Н Ю",
                      curses.color_pair(2) | curses.A_BOLD)
        for key, val in menu.items():
            if key.value == number_menu:
                screen.attron(curses.A_STANDOUT)
            screen.addstr(Constant.HEIGHT // 2 - 4 + key.value, Constant.WIDTH // 2 - 9, val)
            screen.attroff(curses.A_STANDOUT)
        c = screen.getch()
        if c == 10:
            break
        elif c == 65:
            number_menu = number_menu - 2 if number_menu != 1 else 5
        elif c == 66:
            number_menu = number_menu + 2 if number_menu != 5 else 1
        screen.refresh()
    return number_menu


def draw_characteristic(screen: curses.window, character: model.Character):
    screen.attron(curses.color_pair(3))
    screen.addstr(
        Constant.CHARACTERISTIC_VAL_Y,
        Constant.CHARACTERISTIC_VAL_X,
        "Health: {}/{}  ".format(character.health, character.max_health),
    )
    screen.addstr(
        Constant.CHARACTERISTIC_VAL_Y + 1,
        Constant.CHARACTERISTIC_VAL_X,
        "Power: {} ".format(character.power),
    )
    screen.addstr(
        Constant.CHARACTERISTIC_VAL_Y + 2,
        Constant.CHARACTERISTIC_VAL_X,
        "Dexterity: {}     ".format(character.dexterity),
    )
    screen.addstr(
        Constant.CHARACTERISTIC_VAL_Y + 3,
        Constant.CHARACTERISTIC_VAL_X,
        "Current weapon: {}".format(character.weapon.size_object if character.weapon is not None else '-'),
    )
    screen.attroff(curses.color_pair(3))



def draw_health_bar(screen: curses.window, character: model.Character):
    health = character.health // 10
    max_health = character.max_health // 10
    str_health = "Health: ["
    screen.addstr(Constant.HEALTH_BAR_Y, Constant.HEALTH_BAR_X, str_health)
    screen.addstr(
        Constant.HEALTH_BAR_Y,
        Constant.HEALTH_BAR_X + len(str_health),
        "." * health,
        curses.color_pair(8),
    )
    screen.addstr(
        Constant.HEALTH_BAR_Y,
        Constant.HEALTH_BAR_X + len(str_health) + health,
        "-" * (max_health - health),
        curses.color_pair(5),
    )
    screen.addstr(
        Constant.HEALTH_BAR_Y, Constant.HEALTH_BAR_X + len(str_health) + max_health, "]   "
    )
    screen.refresh()


def draw_backpack(screen: curses.window, character: model.Character):
    screen.addstr(
        Constant.BACKPACK_Y - 2,
        Constant.BACKPACK_INF_X + 10,
        "BACKPACK",
        curses.color_pair(3),
    )
    screen.addstr(
        Constant.BACKPACK_Y,
        Constant.BACKPACK_INF_X,
        "Meal in the backpack {}".format(len(character.backpack.meal_list)),
        curses.color_pair(3),
    )
    screen.addstr(
        Constant.BACKPACK_Y + 1,
        Constant.BACKPACK_INF_X,
        "Weapon in the backpack {}".format(len(character.backpack.weapon_list)),
        curses.color_pair(3),
    )
    screen.addstr(
        Constant.BACKPACK_Y + 2,
        Constant.BACKPACK_INF_X,
        "Scroll in the backpack {}".format(len(character.backpack.scroll_list)),
        curses.color_pair(3),
    )
    screen.addstr(
        Constant.BACKPACK_Y + 3,
        Constant.BACKPACK_INF_X,
        "Elixir in the backpack {}".format(len(character.backpack.elixir_list)),
        curses.color_pair(3),
    )
    screen.addstr(
        Constant.BACKPACK_Y + 4,
        Constant.BACKPACK_INF_X,
        "Score {}".format(character.score),
        curses.color_pair(3),
    )


def draw_weapons_list(screen: curses.window, character: model.Character):
    screen.addstr(
        Constant.BACK_CONTENT_Y,
        Constant.BACK_CONTENT_X,
        "Choose the weapon:"
    )
    for i, weapon in enumerate(character.backpack.weapon_list):
        content_line = f"{i + 1} - Weapon size: {weapon.size_object.name}"
        screen.addstr(
            Constant.BACK_CONTENT_Y + i + 1,
            Constant.BACK_CONTENT_X,
            content_line,
        )
    screen.refresh()


def draw_meal_list(screen: curses.window, character: model.Character):
    screen.addstr(
        Constant.BACK_CONTENT_Y,
        Constant.BACK_CONTENT_X,
        "Choose the meal:"
    )
    for i, meal in enumerate(character.backpack.meal_list):
        content_line = f"{i + 1} - size: {meal.size_object.name}"
        screen.addstr(
            Constant.BACK_CONTENT_Y + i + 1,
            Constant.BACK_CONTENT_X,
            content_line,
        )
    screen.refresh()


def draw_elixir_list(screen: curses.window, character: model.Character):
    screen.addstr(
        Constant.BACK_CONTENT_Y,
        Constant.BACK_CONTENT_X,
        "Choose the elixir:"
    )
    for i, elixir in enumerate(character.backpack.elixir_list):
        content_line = f"{i + 1} - size: {elixir.size_object.name}, increase: {elixir.characteristic.name}"
        screen.addstr(
            Constant.BACK_CONTENT_Y + i + 1,
            Constant.BACK_CONTENT_X,
            content_line,
        )
    screen.refresh()


def draw_scroll_list(screen: curses.window, character: model.Character):
    screen.addstr(
        Constant.BACK_CONTENT_Y,
        Constant.BACK_CONTENT_X,
        "Choose the scroll:"
    )
    for i, scroll in enumerate(character.backpack.scroll_list):
        content_line = f"{i + 1} - size: {scroll.size_object.name}, increase: {scroll.characteristic.name}"
        screen.addstr(
            Constant.BACK_CONTENT_Y + i + 1,
            Constant.BACK_CONTENT_X,
            content_line,
        )
    screen.refresh()


def draw_horizontal_line(screen: curses.window):
    for i in range(Constant.WIDTH):
        screen.addstr(
            Constant.BACK_CONTENT_Y - 1,
            i + 1,
            '-',
            curses.color_pair(2),
        )


def view_visible_field(screen: curses.window, visible_map: Visible_map):
    for i in range(dungeon_generation.Constants.MAP_HEIGHT):
        for j in range(dungeon_generation.Constants.MAP_WIDTH):
            if visible_map.playground[i][j] == 'Z':
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(1))
            elif visible_map.playground[i][j] == 'V':
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(5))
            elif visible_map.playground[i][j] == 'G' :
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(4))
            elif visible_map.playground[i][j] == 'O':
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(3))
            elif visible_map.playground[i][j] == 'S':
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(4))
            elif visible_map.playground[i][j] == 'X':
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(1))
            elif visible_map.playground[i][j] == 'J':
                screen.addch(i + 1, j + 1, 'M', curses.color_pair(4))
            elif visible_map.playground[i][j] == 'j':
                screen.addch(i + 1, j + 1, 'm', curses.color_pair(1))
            elif visible_map.playground[i][j] in Constant.OBJECT_VIEW[Type_Object.MEAL]:
                screen.addch(i + 1, j + 1, 'm', curses.color_pair(Constant.COLOR_LIST[Constant.OBJECT_VIEW[
                    Type_Object.MEAL].index(visible_map.playground[i][j])]))
            elif visible_map.playground[i][j] in Constant.OBJECT_VIEW[Type_Object.ELIXIR]:
                screen.addch(i + 1, j + 1, 'e', curses.color_pair(Constant.COLOR_LIST[Constant.OBJECT_VIEW[
                    Type_Object.ELIXIR].index(visible_map.playground[i][j])]))
            elif visible_map.playground[i][j] in Constant.OBJECT_VIEW[Type_Object.SCROLL]:
                screen.addch(i + 1, j + 1, 'c', curses.color_pair(Constant.COLOR_LIST[Constant.OBJECT_VIEW[
                    Type_Object.SCROLL].index(visible_map.playground[i][j])]))
            elif visible_map.playground[i][j] in Constant.OBJECT_VIEW[Type_Object.TREASURE]:
                screen.addch(i + 1, j + 1, 't', curses.color_pair(Constant.COLOR_LIST[Constant.OBJECT_VIEW[
                    Type_Object.TREASURE].index(visible_map.playground[i][j])]))
            elif visible_map.playground[i][j] in Constant.OBJECT_VIEW[Type_Object.WEAPON]:
                screen.addch(i + 1, j + 1, 'w', curses.color_pair(Constant.COLOR_LIST[Constant.OBJECT_VIEW[
                    Type_Object.WEAPON].index(visible_map.playground[i][j])]))
            elif visible_map.playground[i][j] == '.':
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(3))
            else:
                screen.addch(i + 1, j + 1, visible_map.playground[i][j], curses.color_pair(5))
    screen.refresh()


def input_key(next_key, screen, gameplay,visible_map):
    if next_key == ord("w"):
        gameplay.user.direction = model.Direction.Up
    elif next_key == ord("s"):
        gameplay.user.direction = model.Direction.Down
    elif next_key == ord("a"):
        gameplay.user.direction = model.Direction.Left
    elif next_key == ord("d"):
        gameplay.user.direction = model.Direction.Right
    elif next_key == ord("h"):
        draw_weapons_list(screen, gameplay.user)
    elif next_key == ord('j'):
        draw_meal_list(screen, gameplay.user)
    elif next_key == ord("k"):
        draw_elixir_list(screen, gameplay.user)
    elif next_key == ord("e"):
        draw_scroll_list(screen, gameplay.user)
    if next_key in Constant.OBJECT_TYPE:
        number = screen.getch()
        gameplay.user.open_backpack(Constant.OBJECT_TYPE[next_key], number)
        draw_game_field(screen)
        view_visible_field(screen, visible_map)
        draw_addition(screen, gameplay.user)
        add_new_user_pos(screen, gameplay)
    screen.refresh()


def draw_addition(screen: curses.window, character: model.Character):
    draw_health_bar(screen, character)
    draw_characteristic(screen, character)
    draw_horizontal_line(screen)


def draw_game_field(screen: curses.window):
    screen.clear()
    screen.attron(curses.color_pair(2))
    screen.border()
    screen.attroff(curses.color_pair(2))

def init_statistic_screen() -> curses.window:
    stat_screen = curses.newwin(
        dungeon_generation.Constants.MAP_HEIGHT + 10,
        (dungeon_generation.Constants.MAP_WIDTH + 2) // 2 - 7,
        0,
        dungeon_generation.Constants.MAP_WIDTH + 2,
    )
    draw_game_field(stat_screen)
    stat_screen.addstr(1, 10, "Game statistics", curses.color_pair(3))
    return stat_screen


def statistic_screen(stat_screen: curses.window, gameplay: model.Gameplay, game_status, is_continue, is_save_state):
    game_statistic = statistic.GameStatistics(gameplay)
    draw_game_field(stat_screen)
    for i, (name, value) in enumerate(game_statistic.statistic_dict.items(), start=3):
        stat_screen.addstr(i, 3, f"{name}: {value}", curses.color_pair(3))
    draw_backpack(stat_screen, gameplay.user)
    if not is_save_state and (not game_status  or gameplay.user.position == gameplay.exit.position):
        level_stat = statistic.Level_Stat()
        if is_continue:
            level_stat.import_previous()
        level_stat.append_last(game_statistic)
        level_stat.export_to_json()
    if not is_save_state and (not game_status or gameplay.level > 21):
        attempt_stat = statistic.Attempt_Stat()
        attempt_stat.save_attempts(level_stat)
        stat_screen.clear()
    stat_screen.refresh()


def delete_previous_user_pos(screen: curses.window, gameplay: model.Gameplay):
    screen.addch(
        gameplay.user.position.y + 1,
        gameplay.user.position.x + 1,
        gameplay.user.stands_symbol,
    )


def add_new_user_pos(screen: curses.window, gameplay: model.Gameplay):
    screen.addch(
        gameplay.user.position.y + 1,
        gameplay.user.position.x + 1,
        "P",
        curses.color_pair(2),
    )

def save_game_state(gameplay: model.Gameplay):
    gameplay.game_status = False
    game_state = statistic.Save_state()
    game_state.save_attempt(gameplay)

def start_game_loop(screen: curses.window,stat_screen: curses.window, gameplay: model.Gameplay, is_continue: bool):
    draw_game_field(screen)
    visible_map = Visible_map(gameplay)
    is_save_state = False
    statistic_screen(stat_screen, gameplay, gameplay.game_status, is_continue, is_save_state)
    visible_map.add_visited_rooms_corridors()
    view_visible_field(screen, visible_map)
    add_new_user_pos(screen, gameplay)
    draw_addition(screen, gameplay.user)
    while gameplay.user.health > 0:
        next_key = screen.getch()
        if next_key == ord("o"):
            save_game_state(gameplay)
            is_save_state = True
            break
        else:
            input_key(next_key, screen, gameplay,visible_map)

        if next_key in [ord("w"), ord("s"), ord("a"), ord("d")]:
            delete_previous_user_pos(screen, gameplay)
            visible_map.delete_monster()
            gameplay.moving()
            if gameplay.user.health <= 0:
                gameplay.game_status = False
                break
            visible_map.add_visited_rooms_corridors()
            view_visible_field(screen, visible_map)
            draw_addition(screen, gameplay.user)
            if gameplay.user.position == gameplay.exit.position:
                break
            add_new_user_pos(screen, gameplay)
            gameplay.user.cells_amount += 1
            statistic_screen(stat_screen, gameplay, gameplay.game_status, is_continue, is_save_state)
            screen.refresh()
    statistic_screen(stat_screen, gameplay, gameplay.game_status, is_continue, is_save_state)


if __name__ == "__main__":
    curses.wrapper(main)
