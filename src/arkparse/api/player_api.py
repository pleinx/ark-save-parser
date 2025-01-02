from typing import List, Dict
from pathlib import Path
from uuid import UUID
import time
import threading

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.player.ark_player import ArkPlayer
from arkparse.ark_tribe import ArkTribe
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.misc.inventory import Inventory
from arkparse.parsing import ArkBinaryParser
from arkparse.classes.player import Player
from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration
from arkparse.utils import TEMP_FILES_DIR

from arkparse.object_model.misc.dino_owner import DinoOwner
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.object_model.ark_game_object import ArkGameObject

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

    def __init__(self, ftp_config: Path, map: ArkMap, update_frequency = 900, save: AsaSave = None):
        self.players : List[ArkPlayer] = []
        self.tribes : List[ArkTribe] = []
        self.tribe_to_player_map : Dict[int, List[ArkPlayer]] = {}
        self.save: AsaSave = save
        self.pawns: Dict[UUID, ArkGameObject] = None

        if self.save is not None:
            self.__init_pawns()

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

    def __init_pawns(self):
        if self.save is not None:
            pawn_bps = [Player.pawn_female, Player.pawn_male]
            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and name in pawn_bps,
            )
            self.pawns = self.save.get_game_objects(config)

    def dispose(self):
        self.ftp_client.close()

    def __del__(self):
        self.ftp_client.close()

    def __update_files(self):
        new_players = []
        new_tribes = []
        new_tribe_to_player = {}

        self.ftp_client.connect()

        player_files = self.ftp_client.list_all_profile_files()
        tribe_files = self.ftp_client.list_all_tribe_files()

        output_dir = TEMP_FILES_DIR

        for file in player_files:
            path = self.ftp_client.download_profile_file(file.name, output_dir)
            player : ArkPlayer = ArkPlayer(path)
            if self.save is not None:
                player.get_location_and_inventory(self.save, self.pawns)
            new_players.append(player)
            Path(output_dir / file.name).unlink()

        for file in tribe_files:
            output_dir = TEMP_FILES_DIR
            path = self.ftp_client.download_tribe_file(file.name, output_dir)
            tribe = ArkTribe(path)
            players = []
            for id in tribe.member_ids:
                for p in new_players:
                    p: ArkPlayer
                    if p.id_ == id:
                        players.append(p)
                        break
            new_tribes.append(tribe)
            new_tribe_to_player[tribe.tribe_id] = players
            Path(output_dir / file.name).unlink()

        self.players = new_players
        self.tribes = new_tribes
        self.tribe_to_player_map = new_tribe_to_player

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
            if p.name == player or player is None:
                deaths.append(p.nr_of_deaths)
                dict[p.id_] = p.nr_of_deaths

        return self.__calc_stat(deaths, stat_type) if not as_dict else dict
    
    def get_level(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        level = []
        dict = {}

        for p in self.players:
            if p.name == player or player is None:
                level.append(p.stats.level)
                dict[p.id_] = p.stats.level

        return self.__calc_stat(level, stat_type) if not as_dict else dict
    
    def get_xp(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        xp = []
        dict = {}

        for p in self.players:
            if p.name == player or player is None:
                xp.append(p.stats.experience)
                dict[p.id_] = p.stats.experience

        return self.__calc_stat(xp, stat_type) if not as_dict else dict
    
    def get_player_with(self, stat: int, stat_type: int = StatType.HIGHEST):
        istat = self.__get_stat(stat)
        player: ArkPlayer = None
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
            if p.id_ == player_id:
                player = p
                break
        
        return player, value
    
    def get_player_by_platform_name(self, name: str):
        for p in self.players:
            if p.name == name:
                return p
        return None
    
    def get_tribe_of(self, player: ArkPlayer):
        for t in self.tribes:
            if player.tribe == t.tribe_id:
                return t
        return None
    
    def get_as_owner(self, owner_type: int, player_id: int= None, ue5_id: str = None, tribe_id: int = None, tribe_name: str = None):
        player = None
        tribe = None

        for p in self.players:
            if player_id is not None and p.id_ == player_id:
                player = p
                break
            elif ue5_id is not None and p.unique_id == ue5_id:
                player = p
                break
        
        if player is None and tribe_id is None and tribe_name is None:
            raise ValueError("Player not found")
        
        if player:
            tribe = self.get_tribe_of(player)
        else:
            for t in self.tribes:
                if tribe_id is not None and t.tribe_id == tribe_id:
                    tribe = t
                    break
                elif tribe_name is not None and t.name == tribe_name:
                    tribe = t
                    break
        
        if tribe is None:
            raise ValueError("Tribe not found")

        if owner_type == self.OwnerType.OBJECT:
            return ObjectOwner.from_profile(player, tribe)
        elif owner_type == self.OwnerType.DINO:
            return DinoOwner.from_profile(tribe, player)
        return None
    
    def __check_pawns(self, save: AsaSave):
        if save is None and self.save is None:
            raise ValueError("Save not provided")
        
        if save is not None:
            self.save = save
        
        if self.pawns is None:
            self.__init_pawns()
    
    def get_player_pawn(self, player: ArkPlayer, save: AsaSave = None):
        self.__check_pawns(save)
        for _, pawn in self.pawns.items():
            player_id = pawn.get_property_value("LinkedPlayerDataID")
            if player_id == player.id_:
                return pawn
        return None
    
    def get_player_inventory(self, player: ArkPlayer, save: AsaSave = None):
        if player.inventory:
            return player.inventory
        
        self.__check_pawns(save)
        pawn = self.get_player_pawn(player, self.save)
        player.get_location_and_inventory(save, pawn)

        return player.inventory
    
    def get_player_location(self, player: ArkPlayer, save: AsaSave = None):
        if player.location:
            return player.location
        
        self.__check_pawns(save)
        pawn = self.get_player_pawn(player, self.save)
        player.get_location_and_inventory(save, pawn)

        return player.location

    # def add_to_player_inventory(self, player: ArkPlayer, item: ArkGameObject, save: AsaSave = None):
    #     if player is None:
    #         raise ValueError("Player not found")
        
    #     self.__check_pawns(self.save)
    #     inventory: Inventory = self.get_player_inventory(player, self.save)
    #     self.save.add_obj_to_db(item.uuid)
    #     inventory.add_item(item, self.save)

