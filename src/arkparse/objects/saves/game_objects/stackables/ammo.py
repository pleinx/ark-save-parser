
from uuid import UUID
from arkparse.objects.saves.game_objects.misc.inventory_item import InventoryItem
from arkparse.parsing import ArkBinaryParser

class Ammo(InventoryItem):
    def __init__(self, uuid: UUID, binary: ArkBinaryParser):
        super().__init__(uuid, binary)

    def __str__(self):
        return super().to_string("Ammo")

    
