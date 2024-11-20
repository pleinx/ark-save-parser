from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser

@dataclass
class ArkItemNetId:
    id1 : int
    id2 : int

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        byte_buffer.validate_name("ItemID1")
        byte_buffer.validate_name("UInt32Property")
        byte_buffer.validate_uint32(4)
        byte_buffer.validate_uint32(0)
        byte_buffer.validate_byte(0)
        self.id1 = byte_buffer.read_uint32()
        byte_buffer.validate_name("ItemID2")
        byte_buffer.validate_name("UInt32Property")
        byte_buffer.validate_uint32(4)
        byte_buffer.validate_uint32(0)
        byte_buffer.validate_byte(0)
        self.id2 = byte_buffer.read_uint32()
        byte_buffer.validate_name("None")