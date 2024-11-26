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
    inventory: Inventory

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None, save: AsaSave = None):
        super().__init__(uuid, binary, save)

        if binary is not None:
            self.owner = DinoOwner(binary)
            inv_uuid: ObjectReference = self.object.get_property_value("MyInventoryComponent")

            if inv_uuid is None:
                self.inventory = None
            else:
                inv_bin = save.get_game_obj_binary(UUID(inv_uuid.value))
                inv_parser = ArkBinaryParser(inv_bin, save.save_context)
                self.inventory = Inventory(UUID(inv_uuid.value), inv_parser, save=save)

    @staticmethod
    def from_object(obj: ArkGameObject):
        d: TamedDino = TamedDino()

        d.owner = DinoOwner(obj)
        inv_uuid: ObjectReference = obj.get_property_value("MyInventoryComponent")

        if inv_uuid is None:
            d.inventory = None
        else:
            d.inventory = Inventory(UUID(inv_uuid), None, save=None)