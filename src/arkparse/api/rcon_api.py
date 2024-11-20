from rcon import source
from pathlib import Path
import json
from typing import List
from datetime import datetime

class PlayerDataFiles:
    playtime_file_path = None
    player_id_to_name_path = None

    @staticmethod
    def set_files(playtime_file_path: Path, player_id_to_name_path: Path):
        PlayerDataFiles.playtime_file_path = playtime_file_path
        PlayerDataFiles.player_id_to_name_path = player_id_to_name_path

    @staticmethod
    def get_playtime_file_path():
        return PlayerDataFiles.playtime_file_path

    @staticmethod
    def get_player_id_to_name_path():
        return PlayerDataFiles.player_id_to_name_path

class ActivePlayer:
    def __init__(self, string : str):
        split_str = string.split(",")[0].split(".") + [string.split(",")[1]]
        split_str = [x.strip() for x in split_str]

        self.id_to_name = {}
        if PlayerDataFiles.get_player_id_to_name_path() is not None:
            with open(PlayerDataFiles.get_player_id_to_name_path(), 'r') as f:
                self.id_to_name = json.load(f)

        playtime_file_path = PlayerDataFiles.get_playtime_file_path()
        self.playtime_file_path = playtime_file_path
        self.playtime = 0 if not self.playtime_file_path else self.load_playtime()

        self.name = split_str[1]
        self.ue_5_id = split_str[2]
        self.real_life_name = "" if self.ue_5_id not in self.id_to_name else self.id_to_name[self.ue_5_id]
        self.playtime = self.load_playtime()
        

    def __str__(self):
        return f"{self.name} ({self.real_life_name if self.real_life_name != '' else self.ue_5_id})"
    
    def __eq__(self, other: "ActivePlayer"):
        return self.ue_5_id == other.ue_5_id
    
    def get_name(self):
        return self.real_life_name if self.real_life_name != '' else (self.name + "(steam name)")
    
    def load_playtime(self):
        """Load playtime for the player from the playtime file."""
        try:
            with open(self.playtime_file_path, 'r') as f:
                playtime_data = json.load(f)
            return playtime_data.get(self.ue_5_id, 0)
        except FileNotFoundError:
            return 0

    def save_playtime(self):
        """Save the player's playtime to the playtime file."""
        try:
            with open(self.playtime_file_path, 'r') as f:
                playtime_data = json.load(f)
        except FileNotFoundError:
            playtime_data = {}

        playtime_data[self.ue_5_id] = self.playtime
        with open(self.playtime_file_path, 'w') as f:
            json.dump(playtime_data, f)

    def update_playtime(self, add: int):
        """Update the playtime based on the current session."""
        self.playtime += add
        self.save_playtime()

class GameLogEntry:
    time: datetime
    message: str

    class EntryType:
        CHAT = 0
        GAME = 1

    def __init__(self, time: str, message: str):
        self.time = datetime.strptime(time, "%Y.%m.%d_%H.%M.%S")
        self.type = self.EntryType.CHAT if message.startswith("SERVER:") else self.EntryType.CHAT
        self.message = message.replace("SERVER:", '').strip()

    def __str__(self) -> str:
        return f"{self.time}: {self.message}"

    def is_newer_than(self, other: "GameLogEntry"):
        return self.time > other.time
    
class RconApi:

    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

        self.game_log: List[GameLogEntry] = []
        self.last_game_log_entry = None

    def from_config(config: Path) -> "RconApi":
        with open(config, 'r') as config_file:
            config = json.load(config_file)
        return RconApi(config["host"], config["port"], config["password"])

    def send_cmd(self, cmd: str):
        try:
            with source.Client(self.host, self.port, passwd=self.password) as rcon:
                return rcon.run(cmd)
        except Exception as e:
            print(f"Failed to send command: {e}")
            return None
        
    def send_message(self, message: str):
        try:
            with source.Client(self.host, self.port, passwd=self.password) as rcon:
                return self.send_cmd(f"serverchat {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")
            return None
        
    def get_active_players(self, p = False):
        players = []
        response = self.send_cmd("listplayers")
        if response is None:
            print("Server not responding")
            return
        
        for l in response.split("\n"):
            if l.strip() != "":
                if not "No Players Connected" in l:
                    if p:
                        print(l)
                    players.append(ActivePlayer(l))

        return players 
    
    def get_chat(self):
        self.update_game_log()
        return [entry for entry in self.game_log if entry.type == GameLogEntry.EntryType.CHAT]
    
    def update_game_log(self):
        response = self.send_cmd("getgamelog")
        if response is None:
            print("Server not responding")
            return
        if "Server received, But no response!!" in response:
            return
        entries = response.split("\n")
        entries = [e for e in entries if e.strip() != ""]
        log_entries = [GameLogEntry(time=e.split(" ")[0].strip(':'), message=" ".join(e.split(" ")[1:])) for e in entries]
        new_entries = [e for e in log_entries if self.last_game_log_entry is None or e.is_newer_than(self.last_game_log_entry)]
        self.game_log.extend(new_entries)
        self.last_game_log_entry = log_entries[-1] if len(log_entries) else None
        return new_entries
    
    def get_new_chat(self):
        chat = self.get_chat()
        self.update_game_log()
        return [entry for entry in self.game_log if entry.type == GameLogEntry.EntryType.CHAT and entry not in chat]
    
    def get_chat_since(self, since: datetime):
        self.update_game_log()
        return [entry for entry in self.game_log if entry.type == GameLogEntry.EntryType.CHAT and entry.time > since]
