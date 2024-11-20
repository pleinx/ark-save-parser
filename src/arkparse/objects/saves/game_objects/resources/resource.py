
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.objects.saves.game_objects.misc.inventory import Inventory
from arkparse.objects.saves.game_objects.abstract_game_object import AbstractGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.struct.ark_item_net_id import ArkItemNetId

class Resource:
    binary: ArkBinaryParser
    object: AbstractGameObject

    net_id: ArkItemNetId

    owner_inventory: UUID
    quantity: int

    def _get_class_name(self):
        self.binary.set_position(0)
        class_name = self.binary.read_name()
        return class_name

    def __init__(self, uuid: UUID, binary: ArkBinaryParser):
        self.binary = binary
        bp = self._get_class_name()
        self.object = AbstractGameObject(uuid=uuid, blueprint=bp, binary_reader=binary)

        self.net_id = self.object.get_property_value("ItemID")
        self.owner_inventory = UUID(self.object.get_property_value("OwnerInventory").value)
        self.quantity = self.object.get_property_value("ItemQuantity")

        if self.quantity is None:
            self.quantity = 1

    def __str__(self):
        return f"Resource: {self.net_id} ({self.quantity})"
    
    def get_inventory(self, save: AsaSave):
        bin = save.get_game_obj_binary(self.owner_inventory)
        parser = ArkBinaryParser(bin, save.save_context)
        return Inventory(self.owner_inventory, parser, save=save)

    
