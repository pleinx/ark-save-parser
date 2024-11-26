from typing import Dict, List
from uuid import UUID

from arkparse.objects.saves.game_objects.cryopods.cryopod import Cryopod
from arkparse.objects.saves.game_objects.dinos.dino import Dino
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration

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
    
    def get_all_filtered(self, level_lower_bound: int = None, level_upper_bound: int = None, class_name: List[str] = None, tamed: bool = None, include_cryopodded: bool = True, only_cryopodded: bool = False) -> Dict[UUID, Dino]:
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
        
        if level_upper_bound is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.stats.current_level <= level_upper_bound}
        
        if class_name is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.object.blueprint == class_name}

        if tamed is not None:
            if tamed:
                filtered_dinos = {k: v for k, v in filtered_dinos.items() if isinstance(v, TamedDino)}
            else:
                filtered_dinos = {k: v for k, v in filtered_dinos.items() if not isinstance(v, TamedDino)}

        if not include_cryopodded:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if isinstance(v, TamedDino) and v.cryopod is None}

        if only_cryopodded:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if isinstance(v, TamedDino) and v.cryopod is not None}

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
    