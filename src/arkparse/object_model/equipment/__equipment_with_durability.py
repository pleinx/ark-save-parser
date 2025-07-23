
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.classes.equipment import Armor as ArmorBps, Shields as ShieldBps, Saddles as SaddleBps, Weapons, Misc

from .__equipment import Equipment

def _get_default_dura(bp: str) -> float:
    if bp in ArmorBps.chitin.all_bps:
        return 50
    elif bp in ArmorBps.ghillie.all_bps or bp in ArmorBps.leather.all_bps or bp in ArmorBps.desert.all_bps:
        return 45
    elif bp in ArmorBps.fur.all_bps:
        return 125
    elif bp in ArmorBps.cloth.all_bps:
        return 25
    elif bp in ArmorBps.riot.all_bps or bp in ArmorBps.flak.all_bps or bp in ArmorBps.tek.all_bps:
        return 120
    elif bp in ArmorBps.scuba.all_bps:
        return 185
    elif bp in ArmorBps.hazard.all_bps:
        return 85.5
    elif bp == ShieldBps.metal:
        return 1250
    elif bp == ShieldBps.riot:
        return 2300
    elif bp == ShieldBps.wood:
        return 350
    elif bp == ArmorBps.misc.gas_mask:
        return 50
    elif bp == ArmorBps.misc.miners_helmet:
        return 120
    elif bp == ArmorBps.misc.night_vision_goggles:
        return 45
    elif bp in [SaddleBps.tapejara_tek, SaddleBps.rex_tek, SaddleBps.mosa_tek, SaddleBps.megalodon_tek, SaddleBps.rock_drake_tek]:
        return 120
    elif bp == SaddleBps.mole_rat:
        return 500
    elif bp in SaddleBps.all_bps:
        return 100
    elif bp == Weapons.advanced.compound_bow:
        return 55
    elif bp == Weapons.primitive.pike:
        return 40
    elif bp == Weapons.primitive.stone_club:
        return 40
    elif bp == Weapons.primitive.sword:
        return 70
    elif bp == Misc.prod:
        return 10
    elif bp == Weapons.primitive.slingshot:
        return 40
    elif bp == Weapons.primitive.bow:
        return 50
    elif bp == Weapons.primitive.crossbow:
        return 100
    elif bp == Misc.harpoon:
        return 100
    elif bp == Weapons.primitive.simple_pistol:
        return 60
    elif bp == Weapons.advanced.longneck:
        return 70
    elif bp == Weapons.primitive.shotgun:
        return 80
    elif bp == Weapons.advanced.fabricated_pistol:
        return 60
    elif bp == Weapons.advanced.fabricated_shotgun:
        return 120
    elif bp == Weapons.advanced.assault_rifle:
        return 40
    elif bp == Weapons.advanced.fabricated_sniper:
        return 70
    elif bp == Weapons.advanced.rocket_launcher:
        return 120
    elif bp == Weapons.advanced.tek_rifle:
        return 80
    elif bp == Weapons.gathering.sickle:
        return 40
    elif bp == Weapons.gathering.metal_hatchet:
        return 40
    elif bp == Weapons.gathering.metal_pick:
        return 40
    elif bp == Weapons.gathering.stone_hatchet:
        return 40
    elif bp == Weapons.gathering.stone_pick:
        return 40
    elif bp == Weapons.gathering.fishing_rod:
        return 40
    else:
        print(f"WARNING: No durability found for {bp}")
        return 1

class EquipmentWithDurability(Equipment):
    durability: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        dura = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
        self.durability = self.get_actual_value(ArkEquipmentStat.DURABILITY, dura)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat(__stats + [self.get_internal_value(ArkEquipmentStat.DURABILITY)])
    
    def get_implemented_stats(self) -> list:
        return [ArkEquipmentStat.DURABILITY]

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.DURABILITY:
            d = _get_default_dura(self.object.blueprint)
            return int((self.durability - d)/(d*0.00025))
        else:
            raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
        
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.DURABILITY:
            d = _get_default_dura(self.object.blueprint)
            value = d * (0.00025*internal_value + 1)
            return value
        else:
            raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
        
    def set_stat(self, stat: ArkEquipmentStat, value: float, save: AsaSave = None):
        if stat == ArkEquipmentStat.DURABILITY:
            self.__set_durability(value, save)
        else:
            raise ValueError(f"Stat {stat} is not valid for {self.class_name}")

    def __set_durability(self, durability: float, save: AsaSave = None):
        self.durability = durability
        self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.DURABILITY), ArkEquipmentStat.DURABILITY, save)  

    def _get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float, multiplier: float) -> float:
        if stat == ArkEquipmentStat.DURABILITY:
            return round(rating / multiplier, 1)
        else:
            return super()._get_stat_for_rating(stat, rating, multiplier)
