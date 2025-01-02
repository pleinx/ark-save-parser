
from uuid import UUID
import os

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
    class_name: str = "Equipment"

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        self.is_equipped = self.object.get_property_value("bEquippedItem", default=False)
        self.is_bp = self.object.get_property_value("bIsBlueprint", default=False)
        if not self.is_bp:
            self.crafter = ObjectCrafter(self.object)

        self.rating = self.object.get_property_value("ItemRating", default=1)
        self.quality = self.object.get_property_value("ItemQualityIndex", default=ArkItemQuality.PRIMITIVE.value)
        self.current_durability = self.object.get_property_value("SavedDurability", default=1.0)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()
            
    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
    
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
    
    def set_stat(self, stat: ArkEquipmentStat, value: float, save: AsaSave = None):
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
    
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        raise ValueError("Cannot generate equipment from template for base class")
    
    def get_implemented_stats(self) -> list:
        raise ValueError("Cannot get implemented stats for base class") 
    
    def auto_rate(self, save: AsaSave = None):
        raise ValueError("Cannot auto rate for base class equipment")
    
    def get_average_stat(self, __stats = []) -> float:
        return sum(__stats) / len(__stats)

    def __determine_quality_index(self) -> int:
        if self.rating > 10:
            index = ArkItemQuality.ASCENDANT
        elif self.rating > 7:
            index = ArkItemQuality.MASTERCRAFT
        elif self.rating > 4.5:
            index = ArkItemQuality.JOURNEYMAN
        elif self.rating > 2.5:
            index = ArkItemQuality.APPRENTICE
        elif self.rating > 1.25:
            index = ArkItemQuality.RAMSHACKLE
        else:
            index = ArkItemQuality.PRIMITIVE

        return index
    
    def _auto_rate(self, multiplier: float, average_stat: int, save: AsaSave = None):
        self.rating = average_stat * multiplier
        self.quality = self.__determine_quality_index()
        self.set_quality_index(self.quality, save)
        self.set_rating(self.rating, save)

    @staticmethod
    def _generate_from_template(own_class: callable, template_file: str, bp_class: str, save: AsaSave):
        uuid, parser = super()._generate(save, os.path.join("templates", "equipment", template_file))
        parser.replace_bytes(uuid.bytes, position=len(parser.byte_buffer) - 16)
        eq: "Equipment" = own_class(uuid, parser)
        eq.reidentify(uuid, bp_class)
        return eq

    def is_rated(self) -> bool:
        return self.rating > 1  

    def is_crafted(self) -> bool:
        return False if self.crafter is None else self.crafter.is_valid()

    def set_quality_index(self, quality: ArkItemQuality, save: AsaSave = None):
        if self.quality == ArkItemQuality.PRIMITIVE.value:
            raise ValueError("Cannot modify quality of an item with quality 0")
        
        self.quality = quality.value
        self.binary.replace_byte_property(self.binary.set_property_position("ItemQualityIndex"), quality.value)
        self.update_binary(save)

    def set_rating(self, rating: int, save: AsaSave = None):
        if not self.is_rated():
            raise ValueError("Cannot modify rating of a default crafted item")
        
        self.rating = rating
        self.binary.replace_float(self.binary.set_property_position("ItemRating"), rating)
        self.update_binary(save)

    def set_current_durability(self, percentage: float, save: AsaSave = None):
        self.current_durability = percentage / 100
        self.binary.replace_float(self.binary.set_property_position("SavedDurability"), self.current_durability)
        self.update_binary(save)

    def _set_internal_stat_value(self, value: float, position: ArkEquipmentStat, save: AsaSave = None):
        self.binary.replace_u16(self.binary.set_property_position("ItemStatValues", position.value), value)
        self.update_binary(save)

    def get_stat_value(self, position: ArkEquipmentStat) -> int:
        return self.object.get_property_value("ItemStatValues", position=position.value, default=0)
    
    def reidentify(self, new_uuid: UUID = None, new_class: str = None):
        super().reidentify(new_uuid)
        if new_class is not None:
            self.object.change_class(new_class, self.binary)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave, cls: callable = None):
        parser = ArkBinaryParser(item.binary.byte_buffer, save.save_context)
        if cls == None:
            cls = Equipment

        return cls(item.object.uuid, parser)
