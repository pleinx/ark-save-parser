
from uuid import UUID
import math

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.utils.json_utils import DefaultJsonEncoder

from .__equipment import Equipment
from .__equipment_with_durability import EquipmentWithDurability


class Weapon(EquipmentWithDurability):
    damage: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        damage = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DAMAGE.value, default=0)
        self.damage = self.get_actual_value(ArkEquipmentStat.DAMAGE, damage)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)

        self.class_name = "weapon"             
        if binary is not None:
            self.__init_props__()

    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        file = "weapon_bp" if is_bp else "weapon"
        return Equipment._generate_from_template(Weapon, file, class_, save)

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat([self.get_internal_value(ArkEquipmentStat.DAMAGE)])
    
    def get_implemented_stats(self) -> list:
        return super().get_implemented_stats() + [ArkEquipmentStat.DAMAGE]

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.DAMAGE:
            return int((self.damage - 100.0) * 100)
        else:
            return super().get_internal_value(stat)    
        
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.DAMAGE:
            return round(100.0 + internal_value / 100, 1)
        else:
            return super().get_actual_value(stat, internal_value)
        
    def set_stat(self, stat: ArkEquipmentStat, value: float, save: AsaSave = None):
        if stat == ArkEquipmentStat.DAMAGE:
            self.__set_damage(value, save)
        else:
            return super().set_stat(stat, value, save)

    def __set_damage(self, damage: float, save: AsaSave = None):
        self.damage = damage
        self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.DAMAGE), ArkEquipmentStat.DAMAGE, save)

    def auto_rate(self, save: AsaSave = None):
        self._auto_rate(0.000674, self.get_average_stat(), save) 

    def get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float) -> float:
        if stat == ArkEquipmentStat.DAMAGE:
            value = round(rating / 0.000674, 1)
        else:
            value = super()._get_stat_for_rating(stat, rating, 0.000674)

        return self.get_actual_value(stat, value)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave):
        return Equipment.from_inventory_item(item, save, Weapon)

    @staticmethod
    def from_object(obj: ArkGameObject):
        saddle = Weapon()
        saddle.__init_props__(obj)
        
        return saddle

    def __str__(self):
        return f"Weapon: {self.get_short_name()} - Damage: {self.damage} - Durability: {self.durability} - BP: {self.is_bp} - Crafted: {self.is_crafted()} - Rating: {self.rating}"

    def toJsonObj(self):
        return { "UUID": self.object.uuid.__str__() if self.object.uuid is not None else None,
                 "UUID2": self.object.uuid2.__str__() if self.object.uuid2 is not None else None,
                 "ItemNetId1": self.id_.id1 if self.id_ is not None else None,
                 "ItemNetId2": self.id_.id2 if self.id_ is not None else None,
                 "OwnerInventoryUUID": self.owner_inv_uuid.__str__() if self.owner_inv_uuid is not None else None,
                 "ShortName": self.get_short_name(),
                 "ClassName": self.class_name,
                 "ItemArchetype": self.object.blueprint,
                 "ImplementedStats": self.get_implemented_stats().__str__() if self.get_implemented_stats() is not None else None,
                 "bIsBlueprint": self.is_bp,
                 "bEquippedItem": self.is_equipped,
                 "bIsRated": self.is_rated(),
                 "bIsCrafted": self.is_crafted(),
                 "ItemQuantity": self.quantity,
                 "ItemQualityIndex": self.quality,
                 "ItemRating": self.rating,
                 "Damage": self.damage,
                 "Durability": self.durability,
                 "SavedDurability": self.current_durability,
                 "CrafterCharacterName": self.crafter.char_name if self.crafter is not None else None,
                 "CrafterTribeName": self.crafter.tribe_name if self.crafter is not None else None }

    def toJsonStr(self):
        return json.dumps(toJsonObj(), indent=4, cls=DefaultJsonEncoder)
