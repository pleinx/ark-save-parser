#TamedTimeStamp
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.game_objects.misc.dino_owner import DinoOwner
from arkparse.objects.saves.game_objects.misc.inventory import Inventory

from .dino import Dino


class TamedDino(Dino):
    owner: DinoOwner
    inventory: Inventory

    def __init__(self, uuid: UUID, binary: ArkBinaryParser, save: AsaSave):
        super().__init__(uuid, binary, save)
        self.owner = DinoOwner(self.object)

        inv_uuid = self.object.get_property_value("MyInventoryComponent")

        #NumberOfLevelUpPointsAppliedTamed ???

        if inv_uuid is None:
            self.inventory = None
        else:
            inv_bin = save.get_game_obj_binary(UUID(inv_uuid.value))
            inv_parser = ArkBinaryParser(inv_bin, save.save_context)
            self.inventory = Inventory(UUID(inv_uuid.value), inv_parser, save=save)