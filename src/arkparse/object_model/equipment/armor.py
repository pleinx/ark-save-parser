
from uuid import UUID
import math

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.misc.inventory_item import InventoryItem

from .__equipment import Equipment
from .__armor_defaults import _get_default_dura, _get_default_armor, _get_default_hypoT, _get_default_hyperT


class Armor(Equipment):
    armor: float = 0
    durability: float = 0
    hypothermal_insulation: float = 0
    hyperthermal_insulation: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        armor = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.ARMOR.value, default=0)
        dura = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
        hypo = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPOTHERMAL_RESISTANCE.value, default=0)
        hyper = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPERTHERMAL_RESISTANCE.value, default=0)

        self.armor = round(_get_default_armor(self.object.blueprint)*(0.0002*armor + 1), 1)
        self.durability = math.floor(_get_default_dura(self.object.blueprint)*(0.00025*dura + 1))
        self.hypothermal_insulation = round(_get_default_hypoT(self.object.blueprint)*(0.0002*hypo + 1), 1)
        self.hyperthermal_insulation = round(_get_default_hyperT(self.object.blueprint)*(0.0002*hyper + 1), 1)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()

    def get_average_stat(self) -> float:
        return (self.get_internal_value(ArkEquipmentStat.ARMOR) + 
                self.get_internal_value(ArkEquipmentStat.DURABILITY) + 
                self.get_internal_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE) + 
                self.get_internal_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE)) / 4

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.ARMOR:
            d = _get_default_armor(self.object.blueprint)
            return int((self.armor - d)/(d*0.0002))
        elif stat == ArkEquipmentStat.DURABILITY:
            d = _get_default_dura(self.object.blueprint)
            return int((self.durability - d)/(d*0.00025))
        elif stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
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
            raise ValueError(f"Stat {stat} is not valid for saddles")

    def set_armor(self, armor: float, save: AsaSave = None):
        self.armor = armor
        self.set_stat_value(self.get_internal_value(ArkEquipmentStat.ARMOR), ArkEquipmentStat.ARMOR, save) 

    def set_durability(self, durability: float, save: AsaSave = None):
        self.durability = durability
        self.set_stat_value(self.get_internal_value(ArkEquipmentStat.DURABILITY), ArkEquipmentStat.DURABILITY, save)

    def set_hypothermal_insulation(self, hypoT: float, save: AsaSave = None):
        self.hypothermal_insulation = hypoT
        self.set_stat_value(self.get_internal_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE), ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, save)

    def set_hyperthermal_insulation(self, hyperT: float, save: AsaSave = None):
        self.hyperthermal_insulation = hyperT
        self.set_stat_value(self.get_internal_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE), ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, save)

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
        return f"Armor: {self.get_short_name()} - Armor: {self.armor} - Durability: {self.durability} - HypoT: {self.hypothermal_insulation} - HyperT: {self.hyperthermal_insulation} -BP: {self.is_bp} -Crafted: {self.is_crafted()}"
