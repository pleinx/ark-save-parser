import json
from uuid import UUID
import math

from arkparse import AsaSave
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser

from arkparse.classes.equipment import Armor as ArmorBps
from arkparse.classes.equipment import Saddles as SaddleBps

from .__equipment_with_durability import EquipmentWithDurability
from ...utils.json_utils import DefaultJsonEncoder

class EquipmentWithArmor(EquipmentWithDurability):
    armor: float = 0

    @staticmethod
    def get_default_armor(bp: str):
        if bp in ArmorBps.chitin.all_bps:
            return 50
        elif bp in ArmorBps.ghillie.all_bps:
            return 32
        elif bp in ArmorBps.leather.all_bps:
            return 20
        elif bp in ArmorBps.desert.all_bps:
            return 40
        elif bp in ArmorBps.fur.all_bps:
            return 40
        elif bp in ArmorBps.cloth.all_bps:
            return 10
        elif bp in ArmorBps.riot.all_bps:
            return 115
        elif bp in ArmorBps.flak.all_bps:
            return 100
        elif bp in ArmorBps.tek.all_bps:
            return 180
        elif bp in ArmorBps.scuba.all_bps:
            return 1
        elif bp in ArmorBps.hazard.all_bps:
            return 65
        elif bp == ArmorBps.misc.gas_mask:
            return 1
        elif bp == ArmorBps.misc.miners_helmet:
            return 120
        elif bp == ArmorBps.misc.night_vision_goggles:
            return 1
        elif bp in [SaddleBps.tapejara_tek, SaddleBps.rex_tek, SaddleBps.mosa_tek, SaddleBps.megalodon_tek,
                    SaddleBps.rock_drake_tek]:
            return 45
        elif bp in [SaddleBps.paracer, SaddleBps.diplodocus, SaddleBps.bronto, SaddleBps.paracer_platform,
                    SaddleBps.archelon, SaddleBps.carbo]:
            return 20
        elif bp == SaddleBps.titanosaur_platform:
            return 1
        elif bp in SaddleBps.all_bps:
            return 25
        else:
            print(f"WARNING: No armor found for {bp}")
            return 1

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        armor = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.ARMOR.value, default=0)
        self.armor = self.get_actual_value(ArkEquipmentStat.ARMOR, armor)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
         
        if binary is not None:
            self.__init_props__()  

    def get_implemented_stats(self) -> list:
        return super().get_implemented_stats() + [ArkEquipmentStat.ARMOR]

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat(__stats + [self.get_internal_value(ArkEquipmentStat.ARMOR)])

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.ARMOR:
            d = EquipmentWithArmor.get_default_armor(self.object.blueprint)
            return int((self.armor - d)/(d*0.0002))
        else:
            return super().get_internal_value(stat)

    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.ARMOR:
            d = EquipmentWithArmor.get_default_armor(self.object.blueprint)
            return round(d*(0.0002*internal_value + 1), 1)
        else:
            return super().get_actual_value(stat, internal_value)
        
    def set_stat(self, stat: ArkEquipmentStat, value: float, save: AsaSave = None):
        if stat == ArkEquipmentStat.ARMOR:
            self.__set_armor(value, save)
        else:
            return super().set_stat(stat, value, save)
    
    def _get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float, multiplier: float) -> float:
        if stat == ArkEquipmentStat.ARMOR:
            return round(rating / multiplier, 1)
        else:
            return super()._get_stat_for_rating(stat, rating, multiplier)

    def __set_armor(self, armor: float, save: AsaSave = None):
        self.armor = armor
        self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.ARMOR), ArkEquipmentStat.ARMOR, save)

    def to_json_obj(self):
        json_obj = super().to_json_obj()
        json_obj["Armor"] = self.armor
        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), indent=4, cls=DefaultJsonEncoder)
