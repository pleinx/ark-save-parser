
from uuid import UUID
import os

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.misc.inventory_item import InventoryItem

from .__equipment import Equipment
from .__equipment_with_armor import EquipmentWithArmor
from .__armor_defaults import  _get_default_hypoT, _get_default_hyperT


class Armor(EquipmentWithArmor):
    armor: float = 0
    hypothermal_insulation: float = 0
    hyperthermal_insulation: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        hypo = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPOTHERMAL_RESISTANCE.value, default=0)
        hyper = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPERTHERMAL_RESISTANCE.value, default=0)

        self.hypothermal_insulation = self.get_actual_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, hypo)
        self.hyperthermal_insulation = self.get_actual_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, hyper)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        self.class_name = "armor"
        if binary is not None:
            self.__init_props__()

    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        file = "armor_bp" if is_bp else "armor"
        return Equipment._generate_from_template(Armor, file, class_, save)

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat(__stats + [self.get_internal_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE),
                                                   self.get_internal_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE)])
    
    def get_implemented_stats(self) -> list:
        return super().get_implemented_stats() + [ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, ArkEquipmentStat.HYPERTHERMAL_RESISTANCE]

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
            if self.hypothermal_insulation == 0:
                return 0
            d = _get_default_hypoT(self.object.blueprint)
            return int((self.hypothermal_insulation - d)/(d*0.0002))
        elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            if self.hyperthermal_insulation == 0:
                return 0
            d = _get_default_hyperT(self.object.blueprint)
            return int((self.hyperthermal_insulation - d)/(d*0.0002))
        else:
            return super().get_internal_value(stat)
        
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
            if internal_value == 0:
                return 0
            d = _get_default_hypoT(self.object.blueprint)
            return round(d*(0.0002*internal_value + 1), 1)
        elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            if internal_value == 0:
                return 0
            d = _get_default_hyperT(self.object.blueprint)
            return round(d*(0.0002*internal_value + 1), 1)
        else:
            return super().get_actual_value(stat, internal_value)
        
    def set_stat(self, stat: ArkEquipmentStat, value: float, save: AsaSave = None):
        if stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
            self.__set_hypothermal_insulation(value, save)
        elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            self.__set_hyperthermal_insulation(value, save)
        else:
            return super().set_stat(stat, value, save)

    def __set_hypothermal_insulation(self, hypoT: float, save: AsaSave = None):
        self.hypothermal_insulation = hypoT
        self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE), ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, save)

    def __set_hyperthermal_insulation(self, hyperT: float, save: AsaSave = None):
        self.hyperthermal_insulation = hyperT
        self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE), ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, save)

    def auto_rate(self, save: AsaSave = None):
        self._auto_rate(0.000760, self.get_average_stat(), save)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave):
        return Equipment.from_inventory_item(item, save, Armor)

    @staticmethod
    def from_object(obj: ArkGameObject):
        armor = Armor()
        armor.__init_props__(obj)
        
        return armor
    
    def __str__(self):
        return f"Armor: {self.get_short_name()} - Armor: {self.armor} - Durability: {self.durability} - HypoT: {self.hypothermal_insulation} - HyperT: {self.hyperthermal_insulation} -BP: {self.is_bp} -Crafted: {self.is_crafted()} -Quality: {self.quality} -Rating: {self.rating}"
