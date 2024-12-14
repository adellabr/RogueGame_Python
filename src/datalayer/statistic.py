import json
import os
from ..Business_Logic import model

class GameStatistics:
    def __init__(self, gameplay: model.Gameplay):
        self.statistic_dict = {
               "Score": gameplay.user.score,
               "Level": gameplay.level,
               "Killed enemies amount": gameplay.user.killed_enemies_amount,
               "Eaten food amount": gameplay.user.food_amount,
               "Drunk elixir amount": gameplay.user.elixir_amount,
               "Read scroll amount": gameplay.user.scroll_amount,
               "Hits amount": gameplay.user.hits_amount,
               "Missed hits amount": gameplay.user.missed_hits_amount,
               "Passed cells amount": gameplay.user.cells_amount
           }
        
        
class Stat_report:
    def __init__(self):
        self.stat_dict = {}
        self.directory = 'src/game_stats'
        self.filename = ""
    
    def import_previous(self):
        file = '/'.join([self.directory, self.filename])
        if os.path.exists(file) and os.path.getsize(file) > 0:
            with open(file, 'r') as json_file:
                self.stat_dict = json.load(json_file)
                
    def export_to_json(self):
        os.makedirs(self.directory, exist_ok=True)
        file = '/'.join([self.directory, self.filename])
        with open(file, 'w') as json_file:
            json.dump(self.stat_dict, json_file, indent=2)
            
    def append_last(self, game_statistic: GameStatistics):
        pass
            
            
class Level_Stat(Stat_report):
    def __init__(self):
        self.directory = 'src/game_stats'
        self.filename = 'level_statistics.json'
        self.level = 0
        self.stat_dict = {}
    
    def append_last(self, game_statistic: GameStatistics):
        self.level = len(self.stat_dict) + 1
        self.stat_dict[f"Level {self.level}"] = game_statistic.statistic_dict
        
        
class Attempt_Stat(Stat_report):
    def __init__(self):
        self.directory = 'src/game_stats'
        self.filename = 'attempt_statistics.json'
        self.attempt_number = 0
        self.stat_dict = {}
                
    def append_last(self, level_stat: Level_Stat):
        self.attempt_number = len(self.stat_dict) + 1
        total_stat = {
            "Score": 0,
            "Level": level_stat.level,
            "Killed enemies amount": 0,
            "Eaten food amount": 0,
            "Drunk elixir amount": 0,
            "Read scroll amount": 0,
            "Hits amount": 0,
            "Missed hits amount": 0,
            "Passed cells amount": 0
        }
        for level in level_stat.stat_dict.keys():
            for key in level_stat.stat_dict[level].keys():
                if key != "Level":
                    total_stat[key] += level_stat.stat_dict[level][key]
        self.stat_dict[f"Attempt number {self.attempt_number}"] = total_stat
        self.stat_dict = dict(sorted(self.stat_dict.items(), key=lambda item: item[1]["Score"], reverse=True))
            
    def save_attempts(self, level_stat: Level_Stat):
        self.import_previous()
        self.append_last(level_stat)
        self.export_to_json()
          
        
class Save_state():
    def __init__(self):
        self.directory = 'src/game_stats'
        self.filename = 'game_state.json'
        self.import_dict = {}
        self.statistic_dict = {}
    
    def save_attempt(self, gameplay: model.Gameplay):
        self.statistic_dict["Score"] = gameplay.user.score
        self.statistic_dict["Level"] = gameplay.level
        self.statistic_dict["Killed enemies amount"] = gameplay.user.killed_enemies_amount
        self.statistic_dict["Eaten food amount"] = gameplay.user.food_amount
        self.statistic_dict["Drunk elixir amount"] = gameplay.user.elixir_amount
        self.statistic_dict["Read scroll amount"] = gameplay.user.scroll_amount
        self.statistic_dict["Hits amount"] = gameplay.user.hits_amount
        self.statistic_dict["Missed hits amount"] = gameplay.user.missed_hits_amount
        self.statistic_dict["Passed cells amount"] = gameplay.user.cells_amount
        os.makedirs(self.directory, exist_ok=True)
        file = '/'.join([self.directory, self.filename])
        with open(file, 'w') as json_file:
            json.dump(self.statistic_dict, json_file, indent=2)
            
    def import_state(self):
        file = '/'.join([self.directory, self.filename])
        is_exist = False
        if os.path.exists(file) and os.path.getsize(file) > 0:
            with open(file, 'r') as json_file:
                self.import_dict = json.load(json_file)
            is_exist = True
            os.remove(file)
        return is_exist
    
    def update_parameteres(self, gameplay: model.Gameplay):
        gameplay.user.score = self.import_dict["Score"]
        gameplay.user.killed_enemies_amount = self.import_dict["Killed enemies amount"]
        gameplay.user.food_amount = self.import_dict["Eaten food amount"]
        gameplay.user.elixir_amount = self.import_dict["Drunk elixir amount"]
        gameplay.user.scroll_amount = self.import_dict["Read scroll amount"]
        gameplay.user.hits_amount = self.import_dict["Hits amount"]
        gameplay.user.missed_hits_amount = self.import_dict["Missed hits amount"]
        gameplay.user.cells_amount = self.import_dict["Passed cells amount"]
        
            

        
    
