
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat

from .__equipment import Equipment
from .__armor_defaults import _get_default_dura

class Shield(Equipment):
    durability: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        dura = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)

        self.durability = _get_default_dura(self.object.blueprint)*(0.00025*dura + 1)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()

    def get_average_stat(self) -> float:
        return self.get_internal_value(ArkEquipmentStat.DURABILITY)

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.DURABILITY:
            d = _get_default_dura(self.object.blueprint)
            return int((self.durability - d)/(d*0.00025))
        else:
            raise ValueError(f"Stat {stat} is not valid for shields")

    def set_durability(self, durability: float, save: AsaSave = None):
        self.durability = durability
        self.set_stat_value(self.get_internal_value(ArkEquipmentStat.DURABILITY), ArkEquipmentStat.DURABILITY, save)  

    def auto_rate(self, save: AsaSave = None):
        self._auto_rate(0.000519, self.get_average_stat(), save)          

    @staticmethod
    def from_object(obj: ArkGameObject):
        shield = Shield()
        shield.__init_props__(obj)
        
        return shield
