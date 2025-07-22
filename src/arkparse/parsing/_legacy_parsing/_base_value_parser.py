import struct
from typing import List
from uuid import UUID

from ._binary_reader_base import BinaryReaderBase
from arkparse.logging import ArkSaveLogger

class BaseValueParser(BinaryReaderBase):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    def read_int(self) -> int:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an int.")
        result = struct.unpack_from('<i', self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_uint32(self) -> int:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned int.")
        result = struct.unpack_from('<I', self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_uint16(self) -> int:
        if self.position + 2 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned short.")
        result = struct.unpack_from('<H', self.byte_buffer, self.position)[0]
        self.position += 2
        return result

    def read_uint64(self) -> int:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned long.")
        result = struct.unpack_from('<Q', self.byte_buffer, self.position)[0]
        self.position += 8
        return result
    
    def read_int64(self) -> int:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a long.")
        result = struct.unpack_from('<q', self.byte_buffer, self.position)[0]
        self.position += 8
        return result

    def read_bytes(self, count: int) -> bytes:
        if count > len(self.byte_buffer) - self.position:
            ArkSaveLogger.open_hex_view()
            raise ValueError("Attempting to read more bytes than available in the buffer: " + str(count) + " " + str(len(self.byte_buffer) - self.position))
        result = self.byte_buffer[self.position:self.position + count]
        self.position += count
        return result

    def skip_bytes(self, count: int):
        self.position += count

    def read_string(self) -> str:
       
        length = self.read_uint32()
        if length == 0:
            return None

        is_multi_byte = length < 0
        abs_length = abs(length)

        if is_multi_byte:
            result = self.read_chars(abs_length - 1)
            self.skip_bytes(abs_length * 2)
        else:
            pre_read_pos = self.position
            result = self.read_bytes(abs_length - 1).decode('utf-8')
            terminator = self.read_byte()

            if terminator != 0:
                print(f"Terminator is not zero: {terminator}")
                self.position = pre_read_pos
                ArkSaveLogger.enable_debug = True
                ArkSaveLogger.open_hex_view()

        return result

    def read_chars(self, size: int) -> str:
        result = struct.unpack_from(f'<{size}s', self.byte_buffer, self.position)[0].decode('utf-16')
        self.position += size * 2
        return result

    def read_boolean(self) -> bool:
        return self.read_uint16() != 0

    def read_float(self) -> float:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a float.")
        result = struct.unpack_from('<f', self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_double(self) -> float:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a double.")
        result = struct.unpack_from('<d', self.byte_buffer, self.position)[0]
        self.position += 8
        return result

    def read_short(self) -> int:
        if self.position + 2 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a short.")
        result = struct.unpack_from('<h', self.byte_buffer, self.position)[0]
        self.position += 2
        return result

    def read_unsigned_byte(self) -> int:
        return self.read_byte() & 0xFF

    def read_byte(self) -> int:
        if self.position >= len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a byte.")
        result = self.byte_buffer[self.position]
        self.position += 1
        return result

    def read_uuid(self) -> UUID:
        return UUID(bytes=self.read_bytes(16))
    
    def read_uuid_as_string(self) -> str:
        return str(self.read_uuid())

    def peek_int(self) -> int:
        current_position = self.position
        value = self.read_int()
        self.position = current_position
        return value
    
    def read_name(self) -> str:
        if not self.save_context.has_name_table():
            return self.read_string()
        name_id = self.read_uint32()
        name = self.save_context.get_name(name_id)

        if name is None:
            ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()
            raise ValueError(f"Name is None, for name index {hex(name_id)}")

        if name == "NPCZoneVolume" or "NPCZoneVolume_" in name or "_NPCZoneVolume" in name:
            return name + "_" + hex(self.read_int())

        always_zero = self.read_int()

        if always_zero != 0:
            ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()
            raise ValueError(f"Always zero is not zero: {always_zero}, for name {name}")
        
        return name
    
    def peek_name(self) -> str:
        pos = self.position
        name = self.read_name()
        self.position = pos
        return name
    
    def read_strings_array(self) -> List[str]:
        count = self.read_uint32()
        return [self.read_string() for _ in range(count)]

    def read_names(self, name_count: int) -> List[str]:
        names = []
        offsets = []

        for _ in range(name_count):
            if self.save_context.is_read_names_as_strings():
                offsets.append(self.position + 4)
                names.append(self.read_string())
            else:
                names.append(self.read_name())
        return names, offsets
    
    def read_bytes_as_hex(self, data_size: int) -> str:
        # Reads `data_size` bytes from the current position and returns them as a hexadecimal string
        bytes_data = self.read_bytes(data_size)
        return ' '.join(f"{byte:02X}" for byte in bytes_data)