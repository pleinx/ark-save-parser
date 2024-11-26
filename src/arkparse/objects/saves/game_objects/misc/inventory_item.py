from ..ark_game_object import ArkGameObject
from uuid import UUID
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.asa_save import AsaSave

from arkparse.objects.saves.game_objects.misc.__parsed_object_base import ParsedObjectBase
from arkparse.struct.object_reference import ObjectReference
from arkparse.struct.ark_item_net_id import ArkItemNetId

class InventoryItem(ParsedObjectBase):
    binary: ArkBinaryParser
    object: ArkGameObject

    id_: ArkItemNetId
    owner_inv_uuid: UUID
    quantity: int

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        self.id_ = self.object.get_property_value("ItemID")
        self.quantity = self.object.get_property_value("ItemQuantity", default=1)
        owner_in: ObjectReference = self.object.get_property_value("OwnerInventory", default=ObjectReference())
        self.owner_inv_uuid = owner_in.value

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)

        if self.binary is None:
            self.__init_props__()

    def __str__(self):
        return f"InventoryItem(item={self.object.blueprint.split('/')[-1].split('.')[0]}, quantity={self.quantity})"

    def set_quantity(self, quantity: int):
        self.binary.set_property_position("ItemQuantity")
        self.binary.replace_u32(self.binary.position, quantity)

    def get_inventory(self, save: AsaSave):
        from .inventory import Inventory # placed here to avoid circular import
        bin = save.get_game_obj_binary(self.owner_inv_uuid)
        parser = ArkBinaryParser(bin, save.save_context)
        
        return Inventory(self.owner_inv_uuid, parser, save=save)
