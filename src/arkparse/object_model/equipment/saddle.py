
from uuid import UUID
import math

from arkparse import AsaSave
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.inventory_item import InventoryItem

from .__equipment_with_durability import EquipmentWithDurability
from .__saddle_defaults import _get_saddle_armor

class Saddle(EquipmentWithDurability):
    armor: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        armor = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.ARMOR.value, default=0)

        self.armor = self.get_actual_value(ArkEquipmentStat.ARMOR, armor)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)

        self.class_name = "saddle"             
        if binary is not None:
            self.__init_props__()  

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat(__stats + [self.get_internal_value(ArkEquipmentStat.ARMOR)]) 

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.ARMOR:
            d = _get_saddle_armor(self.object.blueprint)
            return int((self.armor - d)/(d*0.0002))
        else:
            super().get_internal_value(stat)
        
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.ARMOR:
            d = _get_saddle_armor(self.object.blueprint)
            return round(d*(0.0002*internal_value + 1), 1)
        else:
            super().get_actual_value(stat, internal_value)
        
    def set_stat(self, stat: ArkEquipmentStat, value: float, save: AsaSave = None):
        if stat == ArkEquipmentStat.ARMOR:
            self.__set_armor(value, save)
        else:
            super().set_stat(stat, value, save)

    def __set_armor(self, armor: float, save: AsaSave = None):
        self.armor = armor
        self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.ARMOR), ArkEquipmentStat.ARMOR, save)   

    def auto_rate(self, save: AsaSave = None):
        self._auto_rate(0.000926, self.get_average_stat(), save)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave):
        return Equipment.from_inventory_item(item, save, Saddle)

    @staticmethod
    def from_object(obj: ArkGameObject):
        saddle = Saddle()
        saddle.__init_props__(obj)
        
        return saddle
    
    def __str__(self):
        return f"Saddle: {self.get_short_name()} - Armor: {self.armor} - Durability: {self.durability} -BP: {self.is_bp} -Crafted: {self.is_crafted()}"
