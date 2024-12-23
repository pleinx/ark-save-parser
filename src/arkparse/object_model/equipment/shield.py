
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

    def set_durability(self, durability: float, save: AsaSave = None):
        self.durability = durability
        d = _get_default_dura(self.object.blueprint)
        self.set_stat_value(int((durability - d)/(d*0.00025)), ArkEquipmentStat.DURABILITY, save)            

    @staticmethod
    def from_object(obj: ArkGameObject):
        shield = Shield()
        shield.__init_props__(obj)
        
        return shield
