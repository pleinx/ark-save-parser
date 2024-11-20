from dataclasses import dataclass, field


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
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    
