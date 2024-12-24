from typing import Dict, List
from uuid import UUID

from arkparse.object_model.equipment import Armor, Saddle, Weapon, Shield
from arkparse.object_model.equipment.__equipment import Equipment
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.misc.object_crafter import ObjectCrafter
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.enums import ArkItemQuality, ArkEquipmentStat
from arkparse.classes.equipment import Equipment as EqClasses

from .general_api import GeneralApi

class EquipmentApi(GeneralApi):
    class Classes:
        WEAPON = Weapon
        SADDLE = Saddle
        ARMOR = Armor
        SHIELD = Shield

    def __init__(self, save: AsaSave):
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and \
                                               (("Weapons" in name and "PrimalItemAmmo" not in name) or \
                                                 "Armor" in name or \
                                                 name in EqClasses.all_bps)
                                                 
        )
        super().__init__(save, config)

    def __get_cls_filter(self, cls: "EquipmentApi.Classes"):
        if cls == self.Classes.WEAPON:
            return EqClasses.weapons.all_bps
        elif cls == self.Classes.SADDLE:
            return EqClasses.saddles.all_bps
        elif cls == self.Classes.ARMOR:
            return EqClasses.armor.all_bps
        elif cls == self.Classes.SHIELD:
            return EqClasses.shield.all_bps
        else:
            return None
    
    def get_all(self, cls: "EquipmentApi.Classes", config: GameObjectReaderConfiguration = None) -> Dict[UUID, Equipment]:
        def is_valid(obj: ArkGameObject):
            is_engram = obj.get_property_value("bIsEngram")
            return not is_engram
        
        _config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: (True if config is None else config.blueprint_name_filter(name)) and name in self.__get_cls_filter(cls)
        )

        return super().get_all(cls, valid_filter=is_valid, config=_config)
    
    def get_by_class(self, cls: "EquipmentApi.Classes", classes: List[str]) -> Dict[UUID, Equipment]:
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and name in classes and name in self.__get_cls_filter(cls)
        )

        return self.get_all(cls, config)
    
    def get_filtered(self, cls: "EquipmentApi.Classes", 
                     no_bluepints: bool = None, only_blueprints: bool = None, 
                     minimum_quality: ArkItemQuality = ArkItemQuality.PRIMITIVE,
                     crafter: ObjectCrafter = None,
                     classes: List[str] = None) -> Dict[UUID, Equipment]:
        if no_bluepints and only_blueprints:
            raise ValueError("Cannot filter by both no_blueprints and only_blueprints")

        if classes is not None:
            equipment: Dict[UUID, Equipment] = self.get_by_class(cls, classes)
        else:
            equipment: Dict[UUID, Equipment] = self.get_all(cls)

        if no_bluepints:
            equipment = {uuid: item for uuid, item in equipment.items() if not item.is_bp}

        if only_blueprints:
            equipment = {uuid: item for uuid, item in equipment.items() if item.is_bp}

        if minimum_quality != ArkItemQuality.PRIMITIVE:
            equipment = {uuid: item for uuid, item in equipment.items() if item.quality >= minimum_quality.value}

        if crafter is not None:
            equipment = {uuid: item for uuid, item in equipment.items() if item.crafter == crafter}

        return equipment
    
    
    def get_count(self, items: Dict[UUID, InventoryItem]) -> int:
        count = 0
        for item in items.values():
            count += item.quantity
        return count
    
    def get_saddles(self, classes: List[str] = None, minimum_armor: int = None, minimum_durability: int = None) -> Dict[UUID, Saddle]:
        saddles: Dict[UUID, Saddle] = self.get_filtered(self.Classes.SADDLE, classes=classes)
        
        if minimum_armor is not None:
            saddles = {uuid: saddle for uuid, saddle in saddles.items() if saddle.armor >= minimum_armor}
        
        if minimum_durability is not None:
            saddles = {uuid: saddle for uuid, saddle in saddles.items() if saddle.durability >= minimum_durability}
        
        return saddles

    def get_weapons(self, classes: List[str] = None, minimum_damage: int = None, minimum_durability: int = None) -> Dict[UUID, Weapon]:
        weapons: Dict[UUID, Weapon] = self.get_filtered(self.Classes.WEAPON, classes=classes)
        
        if minimum_damage is not None:
            weapons = {uuid: weapon for uuid, weapon in weapons.items() if weapon.damage >= minimum_damage}
        
        if minimum_durability is not None:
            weapons = {uuid: weapon for uuid, weapon in weapons.items() if weapon.durability >= minimum_durability}
        
        return weapons
    
    def get_armor(self, classes: List[str] = None, minimum_armor: int = None, minimum_durability: int = None, minimum_cold_resistance: int = None, minimum_heat_resistance: int = None) -> Dict[UUID, Armor]:
        armor: Dict[UUID, Armor] = self.get_filtered(self.Classes.ARMOR, classes=classes)
        
        if minimum_armor is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.armor >= minimum_armor}
        
        if minimum_durability is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.durability >= minimum_durability}
        
        if minimum_cold_resistance is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.hypothermal_insulation >= minimum_cold_resistance}
        
        if minimum_heat_resistance is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.hyperthermal_insulation >= minimum_heat_resistance}
        
        return armor
    
    def modify_equipment(self, eq_class_ : "EquipmentApi.Classes", equipment: Equipment, target_class: str = None, target_stat: ArkEquipmentStat = None, value: float = None, range: tuple[float, float] = None):
        if eq_class_ == self.Classes.WEAPON:
            equipment: Weapon
        elif eq_class_ == self.Classes.SADDLE:
            equipment: Saddle
        elif eq_class_ == self.Classes.ARMOR:
            equipment: Armor
        elif eq_class_ == self.Classes.SHIELD:
            equipment: Shield
        else:
            raise ValueError("Invalid class")
        
        equipment.reidentify(new_class=target_class)
        equipment._set_internal_stat_value