
from uuid import UUID
import math

from arkparse import AsaSave
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser

from .__equipment import Equipment
from .__saddle_defaults import _get_saddle_armor, _get_saddle_dura

class Saddle(Equipment):
    armor: float = 0
    durability: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        armor = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.ARMOR.value, default=0)
        dura = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)

        self.armor = round(_get_saddle_armor(self.object.blueprint)*(0.0002*armor + 1), 1)
        self.durability = math.floor(_get_saddle_dura(self.object.blueprint)*(0.00025*dura + 1))

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()     

    def set_armor(self, armor: float, save: AsaSave = None):
        self.armor = armor
        d = _get_saddle_armor(self.object.blueprint)
        stat_value = int((armor - d)/(d*0.0002))
        self.set_stat_value(stat_value, ArkEquipmentStat.ARMOR, save) 

    def set_durability(self, durability: float, save: AsaSave = None):
        self.durability = durability
        d = _get_saddle_dura(self.object.blueprint)
        stat_value = int((durability - d)/(d*0.00025))
        self.set_stat_value(stat_value, ArkEquipmentStat.DURABILITY, save)     

    @staticmethod
    def from_object(obj: ArkGameObject):
        saddle = Saddle()
        saddle.__init_props__(obj)
        
        return saddle
    
    def __str__(self):
        return f"Saddle: {self.get_short_name()} - Armor: {self.armor} - Durability: {self.durability} -BP: {self.is_bp} -Crafted: {self.is_crafted()}"
