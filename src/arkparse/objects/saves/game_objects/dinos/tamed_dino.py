#TamedTimeStamp
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.game_objects.misc.dino_owner import DinoOwner
from arkparse.objects.saves.game_objects.misc.inventory import Inventory
from arkparse.objects.saves.game_objects.dinos.dino import Dino
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.struct.object_reference import ObjectReference

class TamedDino(Dino):
    owner: DinoOwner
    inv_uuid: UUID
    inventory: Inventory
    tamed_name: str

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        self.tamed_name = self.object.get_property_value("TamedName")
        inv_uuid: ObjectReference = self.object.get_property_value("MyInventoryComponent")

        if inv_uuid is None:
            self.inv_uuid = None
            self.inventory = None
        else:
            self.inv_uuid = UUID(inv_uuid.value)

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None, save: AsaSave = None):
        super().__init__(uuid, binary, save)

        if binary is not None:
            self.__init_props__()

            if self.inv_uuid is not None:
                inv_bin = save.get_game_obj_binary(self.inv_uuid)
                inv_parser = ArkBinaryParser(inv_bin, save.save_context)
                self.inventory = Inventory(self.inv_uuid, inv_parser, save=save)

    @staticmethod
    def from_object(dino_obj: ArkGameObject, status_obj: ArkGameObject):
        d: TamedDino = TamedDino()
        d.__init_props__(dino_obj)

        Dino.from_object(dino_obj, status_obj, d)

        if d.inv_uuid is not None:
            d.inventory = Inventory(d.inv_uuid, None)
