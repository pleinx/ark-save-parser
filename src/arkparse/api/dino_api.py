from typing import Dict, List
from uuid import UUID

from arkparse.objects.saves.game_objects.cryopods.cryopod import Cryopod
from arkparse.objects.saves.game_objects.dinos.dino import Dino
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.objects.saves.game_objects.misc.dino_owner import DinoOwner
from arkparse.ftp.ark_ftp_client import ArkFtpClient

from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.struct.actor_transform import MapCoords
from arkparse.enums import ArkMap, ArkStat
from arkparse.utils import TEMP_FILES_DIR

class DinoApi:
    def __init__(self, save: AsaSave):
        self.save = save
        self.all_objects = None

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        if config is None:
            if self.all_objects is not None:
                return self.all_objects

            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: \
                    name is not None and \
                        (("Dinos/" in name and "_Character_" in name) or \
                        ("PrimalItem_WeaponEmptyCryopod_C" in name)))

        objects = self.save.get_game_objects(config)
        self.all_objects = objects

        return objects
    
    def get_all(self, config = None) -> Dict[UUID, Dino]:
        objects = self.get_all_objects(config)

        dinos = {}

        for key, obj in objects.items():
            dino = None
            if "Dinos/" in obj.blueprint and "_Character_" in obj.blueprint:
                is_tamed = obj.get_property_value("TamedTimeStamp") is not None

                parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
                if is_tamed:
                    dino = TamedDino(obj.uuid, parser, self.save)
                else:
                    dino = Dino(obj.uuid, parser, self.save)
            elif "PrimalItem_WeaponEmptyCryopod_C" in obj.blueprint:
                if not obj.get_property_value("bIsEngram", default=False):
                    cryopod = Cryopod(obj.uuid, ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context))
                    if cryopod.dino is not None:
                        dino = cryopod.dino
            
            if dino is not None:
                dinos[key] = dino

        return dinos
    
    def get_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3, tamed: bool = True, untamed: bool = True) -> Dict[UUID, Dino]:
        dinos = self.get_all()

        filtered_dinos = {}

        for key, dino in dinos.items():
            if isinstance(dino, TamedDino) and dino.cryopod is not None:
                continue

            if dino.location.is_at_map_coordinate(map, coords, tolerance=radius):
                if (tamed and isinstance(dino, TamedDino)) or (untamed and not isinstance(dino, TamedDino)):
                    filtered_dinos[key] = dino

        return filtered_dinos
    
    def get_all_wild(self) -> Dict[UUID, Dino]:
        dinos = self.get_all()
        wild_dinos = {k: v for k, v in dinos.items() if not isinstance(v, TamedDino)}

        return wild_dinos
    
    def get_all_tamed(self) -> Dict[UUID, TamedDino]:
        dinos = self.get_all()
        tamed_dinos = {k: v for k, v in dinos.items() if isinstance(v, TamedDino)}

        return tamed_dinos
    
    def get_all_in_cryopod(self) -> Dict[UUID, TamedDino]:
        dinos = self.get_all()
        cryopod_dinos = {k: v for k, v in dinos.items() if isinstance(v, TamedDino) and v.cryopod is not None}

        return cryopod_dinos
    
    def get_all_by_class(self, class_names: List[str]) -> Dict[UUID, Dino]:
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and name in class_names
        )

        dinos = self.get_all(config)
        class_dinos = {k: v for k, v in dinos.items() if v.object.blueprint in class_names}

        return class_dinos
    
    def get_all_wild_by_class(self, class_name: List[str]) -> Dict[UUID, Dino]:
        dinos = self.get_all_by_class(class_name)
        wild_dinos = {k: v for k, v in dinos.items() if not isinstance(v, TamedDino)}

        return wild_dinos
    
    def get_all_tamed_by_class(self, class_name: List[str]) -> Dict[UUID, TamedDino]:
        dinos = self.get_all_by_class(class_name)
        tamed_dinos = {k: v for k, v in dinos.items() if isinstance(v, TamedDino)}

        return tamed_dinos
    
    def get_all_of_at_least_level(self, level: int) -> Dict[UUID, Dino]:
        dinos = self.get_all()
        level_dinos = {k: v for k, v in dinos.items() if v.stats.current_level >= level}

        return level_dinos
    
    def get_all_wild_of_at_least_level(self, level: int) -> Dict[UUID, Dino]:
        dinos = self.get_all_of_at_least_level(level)
        wild_dinos = {k: v for k, v in dinos.items() if not isinstance(v, TamedDino)}

        return wild_dinos
    
    def get_all_tamed_of_at_least_level(self, level: int) -> Dict[UUID, TamedDino]:
        dinos = self.get_all_of_at_least_level(level)
        tamed_dinos = {k: v for k, v in dinos.items() if isinstance(v, TamedDino)}

        return tamed_dinos
    
    def get_all_with_stat_of_at_least(self, value: int, stat: List[ArkStat] = None) -> Dict[UUID, Dino]:
        dinos = self.get_all()
        filtered_dinos = {}
        
        for key, dino in dinos.items():
            stats_above = dino.stats.get_of_at_least(value)
            if len(stats_above) and (stat is None or any(s in stats_above for s in stat)):
                filtered_dinos[key] = dinos[key]

        return filtered_dinos
    
    def get_all_filtered(self, level_lower_bound: int = None, level_upper_bound: int = None, 
                         class_name: List[str] = None, 
                         tamed: bool = None, 
                         include_cryopodded: bool = True, only_cryopodded: bool = False, 
                         stat_minimum: int = None, stats: List[ArkStat] = None) -> Dict[UUID, Dino]:
        dinos = None

        if class_name is not None:
            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and name in class_name
            )
            dinos = self.get_all(config)
        else:
            dinos = self.get_all()

        filtered_dinos = dinos

        if level_lower_bound is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.stats.current_level >= level_lower_bound}
            # print(f"LowerLvBound - Filtered to {len(filtered_dinos)} dinos")
        
        if level_upper_bound is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.stats.current_level <= level_upper_bound}
            # print(f"UpperLvBound - Filtered to {len(filtered_dinos)} dinos")
        
        if class_name is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.object.blueprint == class_name}
            # print(f"Class - Filtered to {len(filtered_dinos)} dinos")

        if tamed is not None:
            if tamed:
                filtered_dinos = {k: v for k, v in filtered_dinos.items() if isinstance(v, TamedDino)}
                # print(f"Tamed - Filtered to {len(filtered_dinos)} dinos")
            else:
                filtered_dinos = {k: v for k, v in filtered_dinos.items() if not isinstance(v, TamedDino)}
                # print(f"Untamed - Filtered to {len(filtered_dinos)} dinos")

        if not include_cryopodded:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if not(isinstance(v, TamedDino) and v.cryopod is not None)}
            # print(f"IncludeCryopodded - Filtered to {len(filtered_dinos)} dinos")

        if only_cryopodded:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if isinstance(v, TamedDino) and v.cryopod is not None}
            # print(f"OnlyCryopodded - Filtered to {len(filtered_dinos)} dinos")

        if stat_minimum is not None:
            new_filtered_dinos = {}
            for key, dino in filtered_dinos.items():
                stats_above = dino.stats.get_of_at_least(stat_minimum)
                if len(stats_above) and (stats is None or any(s in stats_above for s in stats)):
                    new_filtered_dinos[key] = dinos[key]
            filtered_dinos = new_filtered_dinos
            # print(f"StatMin - Filtered to {len(filtered_dinos)} dinos")

        return filtered_dinos
    
    def count_by_level(self, List: Dict[UUID, Dino]) -> Dict[int, int]:
        levels = {}

        for key, dino in List.items():
            level = dino.stats.current_level
            if level in levels:
                levels[level] += 1
            else:
                levels[level] = 1

        return levels
    
    def count_by_class(self, List: Dict[UUID, Dino]) -> Dict[str, int]:
        classes = {}

        for key, dino in List.items():
            short_name = dino.get_short_name()
            if short_name in classes:
                classes[short_name] += 1
            else:
                classes[short_name] = 1

        return classes
    
    def count_by_tamed(self, List: Dict[UUID, Dino]) -> Dict[bool, int]:
        tamed = {}

        for key, dino in List.items():
            is_tamed = isinstance(dino, TamedDino)
            if is_tamed in tamed:
                tamed[is_tamed] += 1
            else:
                tamed[is_tamed] = 1

        return tamed
    
    def count_by_cryopodded(self, List: Dict[UUID, Dino]) -> Dict[str, int]:
        cryopodded = {
            "all": 0,
        }

        for key, dino in List.items():
            is_cryopodded = isinstance(dino, TamedDino) and dino.cryopod is not None
            if is_cryopodded:
                short_name = dino.get_short_name()
                cryopodded["all"] += 1
                if short_name in cryopodded:
                    cryopodded[short_name] += 1
                else:
                    cryopodded[short_name] = 1

        return cryopodded
    
    def modify_dinos(self, dinos: Dict[UUID, TamedDino], new_owner: DinoOwner = None, ftp_client: ArkFtpClient = None):
        for key, dino in dinos.items():
            if new_owner is not None:
                dino.owner.replace_with(new_owner, dino.binary)
                self.save.modify_obj_in_db(key, dino.binary.byte_buffer)

        if ftp_client is not None:
            self.save.store_db(TEMP_FILES_DIR / "sapi_temp_save.ark")
            ftp_client.connect()
            ftp_client.upload_save_file(TEMP_FILES_DIR / "sapi_temp_save.ark")
            ftp_client.close()

    def create_heatmap(self, resolution: int = 100, dinos: Dict[UUID, TamedDino] = None, classes: List[str] = None, owner: DinoOwner = None, only_tamed: bool = False):
        import math
        import numpy as np

        tamed = None if not only_tamed else True
        if dinos is None:
            dinos = self.get_all_filtered(class_name=classes, tamed=tamed, include_cryopodded=False)

        heatmap = [[0 for _ in range(resolution)] for _ in range(resolution)]
        print(f"Found {len(dinos)} dinos")

        for key, dino in dinos.items():
            if dino.location is None:
                continue

            coords: MapCoords = dino.location.as_map_coords(ArkMap.ABERRATION)

            y = math.floor(coords.long)
            x = math.floor(coords.lat)

            if x < 0 or x >= resolution or y < 0 or y >= resolution:
                continue

            heatmap[x][y] += 1

        return np.array(heatmap)
        
