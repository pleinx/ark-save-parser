from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkRotator:
    pitch: float
    yaw: float
    roll: float

    def __init__(self, binary_data: "ArkBinaryParser"):
        self.pitch = binary_data.read_double()
        self.yaw = binary_data.read_double()
        self.roll = binary_data.read_double()
