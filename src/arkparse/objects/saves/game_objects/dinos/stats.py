from typing import List
from dataclasses import dataclass
from uuid import UUID

from arkparse.objects.saves.game_objects.misc.__parsed_object_base import ParsedObjectBase
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject

STAT_POSITION_MAP = {
    0: 'health',
    1: 'stamina',
    2: 'torpidity',
    3: 'oxygen',
    4: 'food',
    5: 'water',
    6: 'temperature',
    7: 'weight',
    8: 'melee_damage',
    9: 'movement_speed',
    10: 'fortitude',
    11: 'crafting_speed'
}

@dataclass
class StatPoints:
    health: int = 0
    stamina: int = 0
    torpidity: int = 0
    oxygen: int = 0
    food: int = 0
    water: int = 0
    temperature: int = 0
    weight: int = 0
    melee_damage: int = 0
    movement_speed: int = 0
    fortitude: int = 0
    crafting_speed: int = 0

    def __init__(self, object: ArkGameObject = None):
        if object is None:
            return

        for idx, stat in STAT_POSITION_MAP.items():
            value = object.get_property_value("NumberOfLevelUpPointsApplied", position=idx)
            setattr(self, stat, 0 if value is None else value)

    def get_level(self):
        return self.health + self.stamina + self.torpidity + self.oxygen + self.food + \
               self.water + self.temperature + self.weight + self.melee_damage + \
               self.movement_speed + self.fortitude + self.crafting_speed + 1

    def __str__(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
        ]
        return f"Statpoints(points added)([{', '.join(stats)}])"
    
    def to_string_all(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"torpidity={self.torpidity}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"water={self.water}",
            f"temperature={self.temperature}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
            f"movement_speed={self.movement_speed}",
            f"fortitude={self.fortitude}",
            f"crafting_speed={self.crafting_speed}",
        ]
        return f"Statpoints(points added)([{', '.join(stats)}])"

@dataclass
class StatValues:
    health: float = 0
    stamina: float = 0
    torpidity: float = 0
    oxygen: float = 0
    food: float = 0
    water: float = 0
    temperature: float = 0
    weight: float = 0
    melee_damage: float = 0
    movement_speed: float = 0
    fortitude: float = 0
    crafting_speed: float = 0

    def __init__(self, object: ArkGameObject = None):
        if object is None:
            return
        
        for idx, stat in STAT_POSITION_MAP.items():
            value = object.get_property_value("CurrentStatusValues", position=idx)
            setattr(self, stat, 0 if value is None else value)

    def __str__(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
            f"torpor={self.torpidity}",
        ]
        return f"Statvalues(points added)([{', '.join(stats)}])"
    
    def to_string_all(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"torpidity={self.torpidity}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"water={self.water}",
            f"temperature={self.temperature}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
            f"movement_speed={self.movement_speed}",
            f"fortitude={self.fortitude}",
            f"crafting_speed={self.crafting_speed}",
        ]
        return f"Statvalues(points added)([{', '.join(stats)}])"
    
class DinoStats(ParsedObjectBase):
    base_level: int = 0
    current_level: int = 0

    stat_points: StatPoints = StatPoints()
    stat_values: StatValues = StatValues()

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        base_lv = self.object.get_property_value("BaseCharacterLevel")
        self.base_level = 0 if base_lv is None else base_lv
        self.stat_points = StatPoints(self.object)
        self.stat_values = StatValues(self.object)
        self.current_level = self.stat_points.get_level()
    
    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        if binary is None:
            super().__init__(uuid, binary)
            self.__init_props__()

    @staticmethod
    def from_object(obj: ArkGameObject):
        s: DinoStats = DinoStats()
        s.__init_props__(obj)

        return s

    def __str__(self):
        return f"DinoStats(level={self.current_level}"
    
    def to_string_all(self):
        return f"DinoStats(base_level={self.base_level}, level={self.current_level}, \nstat_points={self.stat_points.to_string_all()}, \nstat_values={self.stat_values.to_string_all()})"