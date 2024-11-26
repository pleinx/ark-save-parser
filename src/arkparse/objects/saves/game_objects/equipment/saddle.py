
from uuid import UUID

from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.game_objects.misc.object_crafter import ObjectCrafter
from arkparse.objects.saves.game_objects.misc.inventory_item import InventoryItem

class Saddle(InventoryItem):
    is_equipped: bool
    crafter: ObjectCrafter

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        self.is_equipped = self.object.get_property_value("bEquippedItem", default=False)
        self.crafter = ObjectCrafter(self.object)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
                         
        if binary is not None:
            self.__init_props__()            

    @staticmethod
    def from_object(obj: ArkGameObject):
        saddle = Saddle()
        saddle.__init_props__(obj)
        return saddle
