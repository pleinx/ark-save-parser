
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser

from .__equipment_with_durability import EquipmentWithDurability

class Shield(EquipmentWithDurability):
    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)

        self.class_name = "shield"           
        if binary is not None:
            self.__init_props__()

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat(__stats)

    def auto_rate(self, save: AsaSave = None):
        self._auto_rate(0.000519, self.get_average_stat(), save)          

    @staticmethod
    def from_object(obj: ArkGameObject):
        shield = Shield()
        shield.__init_props__(obj)
        
        return shield
