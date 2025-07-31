import json

from ..ark_game_object import ArkGameObject
from uuid import UUID
from arkparse.parsing import ArkBinaryParser
from arkparse.saves.asa_save import AsaSave

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.parsing.struct.object_reference import ObjectReference
from arkparse.parsing.struct.ark_item_net_id import ArkItemNetId
from arkparse.logging import ArkSaveLogger
from ...utils.json_utils import DefaultJsonEncoder


class InventoryItem(ParsedObjectBase):
    binary: ArkBinaryParser
    object: ArkGameObject

    id_: ArkItemNetId
    owner_inv_uuid: UUID
    quantity: int

    def __init_props__(self):
        super().__init_props__()

        if self.object is not None:
            self.id_ = self.object.get_property_value("ItemID")
            self.quantity = self.object.get_property_value("ItemQuantity", default=1)
            owner_in: ObjectReference = self.object.get_property_value("OwnerInventory", default=ObjectReference())
            self.owner_inv_uuid = UUID(owner_in.value)
        else:
            ArkSaveLogger.warning_log("InventoryItem object is None, cannot initialize properties")

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None, save: AsaSave = None):
        super().__init__(uuid, binary=binary, save=save)

    def __str__(self):
        return f"InventoryItem(item={self.object.blueprint.split('/')[-1].split('.')[0]}, quantity={self.quantity})"

    def reidentify(self, new_uuid: UUID = None, new_class: str = None):
        self.id_.replace(self.binary)
        super().reidentify(new_uuid)
        if new_class is not None:
            self.object.change_class(new_class, self.binary)
            uuid = self.object.uuid if new_uuid is None else new_uuid
            self.object = ArkGameObject(uuid=uuid, blueprint=new_class, binary_reader=self.binary)

    def add_self_to_inventory(self, inv_uuid: UUID):
        old_id = self.owner_inv_uuid
        self.owner_inv_uuid = inv_uuid
        self.binary.byte_buffer = self.binary.byte_buffer.replace(old_id.bytes, inv_uuid.bytes)

    def to_string(self, name = "InventoryItem"):
        return f"{name}({self.get_short_name()}, quantity={self.quantity})"

    def set_quantity(self, quantity: int, save: AsaSave = None):
        self.quantity = quantity
        prop = self.object.find_property("ItemQuantity")
        self.binary.replace_u32(prop, quantity)

        if save is not None:
            save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)

    def get_inventory(self, save: AsaSave):
        from .inventory import Inventory # placed here to avoid circular import
        bin = save.get_game_obj_binary(self.owner_inv_uuid)
        parser = ArkBinaryParser(bin, save.save_context)

        return Inventory(self.owner_inv_uuid, parser, save=save)

    # def get_owner(self, save: AsaSave):
    #     from .inventory import Inventory # placed here to avoid circular import
    #     inv: Inventory = self.get_inventory(save)
    #     return inv.

    def to_json_obj(self):
        return { "id": self.id_.to_json_obj(), "owner_inv_uuid": self.owner_inv_uuid.__str__(), "quantity": self.quantity }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
