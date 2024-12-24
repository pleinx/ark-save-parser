from uuid import UUID
from pathlib import Path

from arkparse.parsing import ArkBinaryParser
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.misc.inventory import Inventory

from .structure import Structure
class StructureWithInventory(Structure):
    inventory_uuid: UUID
    item_count: int
    max_item_count: int

    inventory: Inventory
    db = AsaSave

    def __init__(self, uuid: UUID, binary: ArkBinaryParser, database: AsaSave):
        binary.save_context = database.save_context
        super().__init__(uuid, binary)
        self.db = database

        self.inventory_uuid = UUID(self.object.get_property_value("MyInventoryComponent").value)
        self.item_count = self.object.get_property_value("CurrentItemCount", default=0)
        self.max_item_count = self.object.get_property_value("MaxItemCount")

        inv_reader = ArkBinaryParser(database.get_game_obj_binary(self.inventory_uuid))
        inv_reader.save_context = binary.save_context

        self.inventory = Inventory(self.inventory_uuid, inv_reader, save=database)

    def set_item_quantity(self, quantity: int):
        if self.item_count != None:
            self.binary.replace_u32(self.binary.set_property_position("CurrentItemCount"), quantity)
            self.item_count = quantity
            self.db.modify_game_obj(self.object.uuid, self.binary.byte_buffer)

    def add_item(self, item: UUID):
        if self.item_count == self.max_item_count:
            return
        
        self.set_item_quantity(self.item_count + 1)
        self.inventory.add_item(item)
        self.db.modify_game_obj(self.inventory.object.uuid, self.inventory.binary.byte_buffer)

    def remove_item(self, item: UUID):
        if self.item_count == 0:
            return

        self.set_item_quantity(self.item_count - 1)
        self.inventory.remove_item(item)
        self.db.modify_game_obj(self.object.uuid, self.binary.byte_buffer)
        self.db.modify_game_obj(self.inventory.object.uuid, self.inventory.binary.byte_buffer)
        self.db.remove_obj_from_db(item)

    def clear_items(self):
        self.set_item_quantity(0)

        for item in self.inventory.items:
            self.db.remove_obj_from_db(item)

        self.inventory.clear_items()
        self.db.modify_game_obj(self.inventory.object.uuid, self.inventory.binary)

    def store_binary(self, path: Path):
        super().store_binary(path)
        self.inventory.store_binary(path)
