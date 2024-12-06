
from uuid import UUID
import math

from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat

from .__equipment import Equipment
from .__weapon_defaults import _get_weapon_dura


class Weapon(Equipment):
    damage: float = 0
    durability: float = 0

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)
            
        durability = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
        damage = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DAMAGE.value, default=0)

        self.damage = round(100.0 + damage / 100, 1)
        self.durability = math.floor(_get_weapon_dura(self.object.blueprint) * (0.00025*durability + 1))

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()            

    @staticmethod
    def from_object(obj: ArkGameObject):
        saddle = Weapon()
        saddle.__init_props__(obj)
        
        return saddle
