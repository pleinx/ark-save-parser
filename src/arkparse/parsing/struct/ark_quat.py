from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkQuat:
    x: float
    y: float
    z: float
    w: float

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        self.x = byte_buffer.read_double()
        self.y = byte_buffer.read_double()
        self.z = byte_buffer.read_double()
        self.w = byte_buffer.read_double()
