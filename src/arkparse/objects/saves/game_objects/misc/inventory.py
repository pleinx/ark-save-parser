from dataclasses import dataclass
from uuid import UUID
from typing import List, Dict

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.objects.saves.game_objects import ArkGameObject
from arkparse.struct import get_uuid_reference_bytes
from arkparse.parsing import ArkBinaryParser

from .inventory_item import InventoryItem
# items array InventoryItems -> ArrayProperty -> ObjectProperty

@dataclass
class Inventory:
    binary: ArkBinaryParser
    object: ArkGameObject
    items: Dict[UUID, InventoryItem]

    container_uuid: UUID
    container_type: str

    def _get_class_name(self):
        self.binary.set_position(0)
        class_name = self.binary.read_name()
        return class_name

    def __init__(self, uuid: UUID, binary: ArkBinaryParser, container_type: str = None, save: AsaSave = None):
        self.binary = binary
        bp = self._get_class_name()
        self.object: ArkGameObject = ArkGameObject(uuid=uuid, blueprint=bp, binary_reader=binary)
        self.items = {}

        item_arr = self.object.get_array_property_value("InventoryItems")
        for item in item_arr:
            item_uuid = UUID(item.value)
            reader = ArkBinaryParser(save.get_game_obj_binary(item_uuid), save.save_context)
            item = InventoryItem(item_uuid, reader, container_type)
            is_engram = item.object.get_property_value("bIsEngram")
            if is_engram is None or not is_engram:
                self.items[item_uuid] = item

    def add_item(self, item: UUID):
        if len(self.items) == 0:
            self.binary.set_property_position("bInitializedMe")
        else:
            self.binary.set_property_position("InventoryItems")


        self.items.append(item)
        
        object_references = []
        for item in self.items:
            object_references.append(get_uuid_reference_bytes(item))
        
        self.binary.replace_array("InventoryItems", "ObjectProperty", object_references)

    def remove_item(self, item: UUID):
        if len(self.items) == 0:
            return

        self.items.remove(item)
        self.binary.set_property_position("InventoryItems")
        
        object_references = []
        for item in self.items:
            object_references.append(get_uuid_reference_bytes(item))
        
        self.binary.replace_array("InventoryItems", "ObjectProperty", object_references if len(object_references) > 0 else None)

    def clear_items(self):
        if len(self.items) == 0:
            return
        
        self.items = []
        self.binary.set_property_position("InventoryItems")
        self.binary.replace_array("InventoryItems", "ObjectProperty", None)

    def __str__(self):
        out = f"Inventory(container={self.container_uuid}, items={len(self.items)})"
              
        for item in self.items:
            out += "\n   - " + str(list(item.values())[0])

        return out
