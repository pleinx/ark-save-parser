from rcon import source
from pathlib import Path
import json
from typing import List
from datetime import datetime
import re

class PlayerDataFiles:
    players_files_path = None

    @staticmethod
    def set_files(players_files_path: Path):
        PlayerDataFiles.players_files_path = players_files_path

class ActivePlayer:
    def __init__(self, string : str):
        split_str = string.split(",")[0].split(".") + [string.split(",")[1]]
        split_str = [x.strip() for x in split_str]
        self.name = split_str[1]
        self.ue_5_id = split_str[2]

        self.id_to_name = {}
        if PlayerDataFiles.players_files_path is not None:
            with open(PlayerDataFiles.players_files_path, 'r') as f:
                id_to_name = json.load(f)
                if self.ue_5_id in id_to_name:
                    self.real_life_name = "" if self.ue_5_id not in id_to_name else "" if "real_name" \
                        not in id_to_name[self.ue_5_id] else id_to_name[self.ue_5_id]["real_name"]

        players_files_path = PlayerDataFiles.players_files_path
        self.players_files_path = players_files_path
        self.playtime = 0 if not self.players_files_path else self.load_playtime()
        
    def __str__(self):
        return f"{self.name} ({self.real_life_name if self.real_life_name != '' else self.ue_5_id})"
    
    def __eq__(self, other: "ActivePlayer"):
        return self.ue_5_id == other.ue_5_id
    
    def get_name(self):
        return self.real_life_name if self.real_life_name != '' else (self.name + "(steam name)")
    
    def load_playtime(self):
        """Load playtime for the player from the playtime file."""
        try:
            with open(self.players_files_path, 'r') as f:
                playtime_data = json.load(f)

                if self.ue_5_id not in playtime_data:
                    return 0
                
                return playtime_data[self.ue_5_id]["playtime"]
        except FileNotFoundError:
            return 0

    def save_playtime(self):
        """Save the player's playtime to the playtime file."""
        try:
            with open(self.players_files_path, 'r') as f:
                player_data = json.load(f)
        except FileNotFoundError:
            player_data = {}

        player_data[self.ue_5_id]["playtime"] = self.playtime
        with open(self.players_files_path, 'w') as f:
            json.dump(player_data, f, indent=4)

    def update_playtime(self, add: int):
        """Update the playtime based on the current session."""
        self.playtime += add
        self.save_playtime()

class GameLogEntry:
    time: datetime
    message_prefix: str
    message: str

    class EntryType:
        CHAT = 0
        GAME = 1
        PLAYER = 2

    def get_player_chat_name(self):
        steam_name = self.message_prefix.split(" ")[0]
        if PlayerDataFiles.players_files_path is not None:
            with open(PlayerDataFiles.players_files_path, 'r') as f:
                players = json.load(f)
                for id in players.keys():
                    p = players[id]
                    if p["steam_name"] == steam_name:
                        if "real_name" in p:
                            return p["real_name"]
        return steam_name
    
    def __get_type(self, message: str) -> EntryType:       
        if message.startswith("SERVER:"):
            return self.EntryType.GAME
        
        match = re.match(r"(\d+)\s\(([^)]+)\):", message)
        if match:
            return self.EntryType.PLAYER

        return self.EntryType.CHAT

    def __init__(self, time: str, message: str):
        self.time = datetime.strptime(time, "%Y.%m.%d_%H.%M.%S")
        self.type = self.__get_type(message)
        
        if self.type == self.EntryType.PLAYER or self.type == self.EntryType.GAME:
            self.message_prefix = message.split(":")[0]
            self.message = ''.join(message.split(":")[1:]).strip()
        else:
            self.message = message
            self.message_prefix = ""

    def __str__(self) -> str:
        return f"{self.__type_str__()}{self.time}: {self.message}"

    def __type_str__(self) -> str:
        if self.type == self.EntryType.PLAYER:
            return ("[" + self.get_player_chat_name() + "]")
        return "[CHAT]" if self.type == self.EntryType.CHAT else "[GAME]"

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
            with source.Client(self.host, self.port, passwd=self.password, timeout=3) as rcon:
                return rcon.run(cmd)
        except Exception as e:
            print(f"Failed to send command: {e}")
            return None
        
    def send_message(self, message: str):
        return self.send_cmd(f"serverchat [BOT] {message}")
    
        
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
