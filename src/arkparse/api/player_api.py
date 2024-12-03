from typing import List
from pathlib import Path
import time
import threading

from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.objects.player.ark_profile import ArkProfile
from arkparse.objects.tribe.ark_tribe import ArkTribe
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes.player import Player
from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration
from arkparse.utils import TEMP_FILES_DIR

from arkparse.objects.saves.game_objects.misc.dino_owner import DinoOwner
from arkparse.objects.saves.game_objects.misc.object_owner import ObjectOwner

class PlayerApi:
    class StatType:
        LOWEST = 0
        HIGHEST = 1
        AVERAGE = 2
        TOTAL = 3

    class Stat:
        DEATHS = 0
        LEVEL = 1
        XP = 2

    class OwnerType:
        OBJECT = 0
        DINO = 1

    def __init__(self, ftp_config: Path, map: FtpArkMap, update_frequency = 900, save: AsaSave = None):
        self.players : List[ArkProfile] = []
        self.tribes : List[ArkTribe] = []
        self.save: AsaSave = save
        self.pawns = None

        if save is not None:
            pawn_bps = [Player.pawn_female, Player.pawn_male]
            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and name in pawn_bps,
            )
            self.pawns = save.get_game_objects(config)

        self.ftp_client : ArkFtpClient = ArkFtpClient.from_config(ftp_config, map)
        
        self.__update_files()
        self.__initial_run = True

        def update_loop():
            while True:
                if self.__initial_run:
                    self.__initial_run = False
                else:
                    self.__update_files()
                time.sleep(update_frequency)

        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

    def dispose(self):
        self.ftp_client.close()

    def __del__(self):
        self.ftp_client.close()

    def __update_files(self):
        new_players = []
        new_tribes = []

        self.ftp_client.connect()

        player_files = self.ftp_client.list_all_profile_files()
        tribe_files = self.ftp_client.list_all_tribe_files()

        output_dir = TEMP_FILES_DIR

        for file in player_files:
            path = self.ftp_client.download_profile_file(file.name, output_dir)
            player : ArkProfile = ArkProfile(path)
            if self.save is not None:
                player.get_location_and_inventory(self.save, self.pawns)
            new_players.append(player)
            Path(output_dir / file.name).unlink()

        for file in tribe_files:
            output_dir = TEMP_FILES_DIR
            path = self.ftp_client.download_tribe_file(file.name, output_dir)
            new_tribes.append(ArkTribe(path))
            Path(output_dir / file.name).unlink()

        self.players = new_players
        self.tribes = new_tribes

        self.ftp_client.close()

    def __calc_stat(self, stat: List[int], stat_type: int):
        if stat_type == self.StatType.LOWEST:
            return min(stat)
        elif stat_type == self.StatType.HIGHEST:
            return max(stat)
        elif stat_type == self.StatType.AVERAGE:
            return sum(stat) / len(stat)
        elif stat_type == self.StatType.TOTAL:
            return sum(stat)
        
    def __get_stat(self, stat: int):
        if stat == self.Stat.DEATHS:
            return self.get_deaths(as_dict=True)
        elif stat == self.Stat.LEVEL:
            return self.get_level(as_dict=True)
        elif stat == self.Stat.XP:
            return self.get_xp(as_dict=True)
        
    def get_deaths(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        deaths = []
        dict = {}

        for p in self.players:
            if p.player_data.name == player or player is None:
                deaths.append(p.player_data.nr_of_deaths)
                dict[p.player_data.id_] = p.player_data.nr_of_deaths

        return self.__calc_stat(deaths, stat_type) if not as_dict else dict
    
    def get_level(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        level = []
        dict = {}

        for p in self.players:
            if p.player_data.name == player or player is None:
                level.append(p.player_data.stats.level)
                dict[p.player_data.id_] = p.player_data.stats.level

        return self.__calc_stat(level, stat_type) if not as_dict else dict
    
    def get_xp(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        xp = []
        dict = {}

        for p in self.players:
            if p.player_data.name == player or player is None:
                xp.append(p.player_data.stats.experience)
                dict[p.player_data.id_] = p.player_data.stats.experience

        return self.__calc_stat(xp, stat_type) if not as_dict else dict
    
    def get_player_with(self, stat: int, stat_type: int = StatType.HIGHEST):
        istat = self.__get_stat(stat)
        player: ArkProfile = None
        value: int = 0
        
        if stat_type == self.StatType.LOWEST:
            player_id = min(istat, key=istat.get)
            value = istat[player_id]
        elif stat_type == self.StatType.HIGHEST:
            player_id = max(istat, key=istat.get)
            value = istat[player_id]
        elif stat_type == self.StatType.AVERAGE:
            player_id = max(istat, key=istat.get)
            value = istat[player_id]
        elif stat_type == self.StatType.TOTAL:
            player_id = max(istat, key=istat.get)
            value = istat[player_id]

        for p in self.players:
            if p.player_data.id_ == player_id:
                player = p
                break
        
        return player, value
    
    def get_player_by_platform_name(self, name: str):
        for p in self.players:
            if p.player_data.name == name:
                return p
        return None
    
    def get_tribe_of(self, player: ArkProfile):
        for t in self.tribes:
            if player.player_data.tribe == t.tribe_data.tribe_id:
                return t
        return None
    
    def get_as_owner(self, owner_type: int, player_id: int= None, ue5_id: str = None):
        player = None
        tribe = None

        for p in self.players:
            if player_id is not None and p.player_data.id_ == player_id:
                player = p
                break
            elif ue5_id is not None and p.player_data.unique_id == ue5_id:
                player = p
                break
        
        if player is None:
            raise ValueError("Player not found")
        
        tribe = self.get_tribe_of(player)

        if owner_type == self.OwnerType.OBJECT:
            return ObjectOwner.from_profile(player, tribe)
        elif owner_type == self.OwnerType.DINO:
            return DinoOwner.from_profile(tribe, player)
        return None

