from ..abstract_game_object import AbstractGameObject
from uuid import UUID
from arkparse.parsing import ArkBinaryParser

class InventoryItem:
    binary: ArkBinaryParser
    object: AbstractGameObject

    inventory_uuid: UUID
    container_uuid: UUID
    quantity: int

    def _get_class_name(self):
        self.binary.set_position(0)
        self.binary.read_name()

    def __init__(self, uuid: UUID, binary: ArkBinaryParser, container_type: str = None):
        self.binary = binary
        bp = self._get_class_name()
        self.object = AbstractGameObject(uuid=uuid, blueprint=bp, binary_reader=binary)
        self.quantity = self.object.get_property_value("ItemQuantity")

    def set_quantity(self, quantity: int):
        self.binary.set_property_position("ItemQuantity")
        self.binary.replace_u32(self.binary.position, quantity)

    def __str__(self):
        return f"InventoryItem(item={self.object.blueprint.split('/')[-1].split('.')[0]}, quantity={self.quantity})"
