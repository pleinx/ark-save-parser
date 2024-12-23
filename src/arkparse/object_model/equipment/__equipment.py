
from uuid import UUID

from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.object_crafter import ObjectCrafter
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.enums import ArkItemQuality, ArkEquipmentStat
from arkparse.saves.asa_save import AsaSave

class Equipment(InventoryItem):
    is_equipped: bool = False
    is_bp: bool = False
    crafter: ObjectCrafter = None
    rating: float = 1
    quality: int = ArkItemQuality.PRIMITIVE.value
    current_durability: float = 1.0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        self.is_equipped = self.object.get_property_value("bEquippedItem", default=False)
        self.is_bp = self.object.get_property_value("bIsBlueprint", default=False)
        if not self.is_bp:
            self.crafter = ObjectCrafter(self.object)

        self.rating = self.object.get_property_value("ItemRatingIndex", default=1)
        self.quality = self.object.get_property_value("ItemQualityIndex", default=ArkItemQuality.PRIMITIVE.value)
        self.current_durability = self.object.get_property_value("SavedDurability", default=1.0)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()

    def is_rated(self) -> bool:
        return self.rating > 1  

    def is_crafted(self) -> bool:
        return False if self.crafter is None else self.crafter.is_valid()

    def modify_quality(self, quality: int, save: AsaSave = None):
        if self.quality == 0:
            raise ValueError("Cannot modify quality of an item with quality 0")
        
        self.quality = quality
        self.binary.replace_bytes(quality.to_bytes(1, byteorder="little"), position=self.binary.set_property_position("ItemQualityIndex"))
        self.update_binary(save)

    def modify_rating(self, rating: int, save: AsaSave = None):
        if not self.is_rated():
            raise ValueError("Cannot modify rating of a default crafted item")
        
        self.rating = rating
        self.binary.replace_float(self.binary.set_property_position("ItemRating"), rating)
        self.update_binary(save)

    def set_current_durability(self, percentage: float, save: AsaSave = None):
        self.current_durability = percentage / 100
        self.binary.replace_float(self.binary.set_property_position("SavedDurability"), self.current_durability)
        self.update_binary(save)

    def set_stat_value(self, value: float, position: ArkEquipmentStat, save: AsaSave = None):
        self.binary.replace_u16(self.binary.set_property_position("ItemStatValues", position.value), value)
        self.update_binary(save)

    def get_stat_value(self, position: ArkEquipmentStat) -> int:
        return self.object.get_property_value("ItemStatValues", position=position.value, default=0)
    
    def reidentify(self, new_uuid: UUID = None, new_class: str = None):
        super().reidentify(new_uuid)
        if new_class is not None:
            self.object.change_class(new_class, self.binary)

