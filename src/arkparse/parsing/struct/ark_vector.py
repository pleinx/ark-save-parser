from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from struct import pack

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkVector:
    x: float = field(default=0.0)
    y: float = field(default=0.0)
    z: float = field(default=0.0)

    def __init__(self, byte_buffer: "ArkBinaryParser" = None, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        if byte_buffer:
            self.x = byte_buffer.read_double()
            self.y = byte_buffer.read_double()
            self.z = byte_buffer.read_double()
        else:
            self.x = x
            self.y = y
            self.z = z

    def to_bytes(self) -> bytes:
        return pack('<ddd', self.x, self.y, self.z)

    def __str__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"
    
