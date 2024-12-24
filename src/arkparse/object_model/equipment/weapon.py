
from uuid import UUID
import math

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.misc.inventory_item import InventoryItem

from .__equipment import Equipment
from .__weapon_defaults import _get_weapon_dura


class Weapon(Equipment):
    damage: float = 0
    durability: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        durability = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
        damage = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DAMAGE.value, default=0)

        self.damage = round(100.0 + damage / 100, 1)
        self.durability = math.floor(_get_weapon_dura(self.object.blueprint) * (0.00025*durability + 1))

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()

    def get_average_stat(self) -> float:
        return (self.get_internal_value(ArkEquipmentStat.DAMAGE) +
                self.get_internal_value(ArkEquipmentStat.DURABILITY)) / 2

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.DAMAGE:
            return int((self.damage - 100.0) * 100)
        elif stat == ArkEquipmentStat.DURABILITY:
            d = _get_weapon_dura(self.object.blueprint)
            return int((self.durability - d)/(d*0.00025))
        else:
            raise ValueError(f"Stat {stat} is not valid for weapons")

    def set_damage(self, damage: float, save: AsaSave = None):
        self.damage = damage
        self.set_stat_value(self.get_internal_value(ArkEquipmentStat.DAMAGE), ArkEquipmentStat.DAMAGE, save)

    def set_durability(self, durability: float, save: AsaSave = None):
        self.durability = durability
        self.set_stat_value(self.get_internal_value(ArkEquipmentStat.DURABILITY), ArkEquipmentStat.DURABILITY, save)

    def auto_rate(self, save: AsaSave = None):
        self._auto_rate(0.000674, self.get_average_stat(), save) 

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave):
        return Equipment.from_inventory_item(item, save, Weapon)

    @staticmethod
    def from_object(obj: ArkGameObject):
        saddle = Weapon()
        saddle.__init_props__(obj)
        
        return saddle
    
    def __str__(self):
        return f"Weapon: {self.get_short_name()} - Damage: {self.damage} - Durability: {self.durability} -BP: {self.is_bp} -Crafted: {self.is_crafted()}"
