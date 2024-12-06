from ._property_insertor import PropertyInsertor
from arkparse.logging import ArkSaveLogger
from typing import Dict, List
import struct


class PropertyReplacer(PropertyInsertor):
    

    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    def set_property_position(self, property_name: str, position: int = 0) -> int:
        if self.save_context is None:
            raise ValueError("Save context is not set")
        
        cur_pos = 0

        for i in range(self.size() - 4):
            self.set_position(i)
            int_value = self.read_uint32()
            if int_value not in self.save_context.names:
                continue
            name = self.save_context.names[int_value]
            if name is not None and name == property_name:
                if cur_pos == position:
                    ArkSaveLogger.debug_log(f"Found property: {name} at {self.read_bytes_as_hex(4)} (position {i})")
                    self.set_position(i)
                    return i
                cur_pos += 1
        return None   

    def replace_string(self, property_position : int, value: str):
        original_position = self.get_position()
        self.set_position(property_position)

        new_length = len(value) + 1
        new_length_byte = (new_length + 4).to_bytes(1, byteorder="little")

        # ArkSaveLogger.enable_debug = True
        # ArkSaveLogger.set_file(self, "debug.bin")
        # ArkSaveLogger.open_hex_view(True)

        self.read_name() # skip prop name
        self.validate_name("StrProperty")
        full_length_pos = self.position
        self.read_byte() # full length
        self.validate_uint64(0)
        string_pos = self.position
        current_string = self.read_string()
        current_nr_of_bytes = len(current_string) + 4

        # replace total length
        self.replace_bytes(full_length_pos, new_length_byte, 1)

        # replace string
        lengthu32 = new_length.to_bytes(4, byteorder="little")
        self.replace_bytes(string_pos, lengthu32 + value.encode("utf-8"), current_nr_of_bytes)

        self.set_position(original_position)
        # print(f"Replaced string {current_string} (length={current_nr_of_bytes}) at {property_position} with {value} at {string_pos}")

    def replace_u16(self, property_position : int, new_value: int):
        value_pos = property_position + 8 + 8 + 1 + 8
        new_value_bytes = new_value.to_bytes(2, byteorder="little")
        self.replace_bytes(value_pos, new_value_bytes)

    def replace_u32(self, property_position : int, new_value: int):
        value_pos = property_position + 8 + 8 + 1 + 8
        new_value_bytes = new_value.to_bytes(4, byteorder="little")
        self.replace_bytes(value_pos, new_value_bytes)

    def replace_u64(self, property_position : int, new_value: int):
        value_pos = property_position + 8 + 8 + 1 + 8
        new_value_bytes = new_value.to_bytes(8, byteorder="little")
        self.replace_bytes(value_pos, new_value_bytes)

    def replace_float(self, property_position : int, new_value: float):
        value_pos = property_position + 8 + 8 + 1 + 8
        new_value_bytes = struct.pack('<f', new_value)
        self.replace_bytes(value_pos, new_value_bytes)

    def replace_double(self, property_position : int, new_value: float):
        value_pos = property_position + 8 + 8 + 1 + 8
        new_value_bytes = struct.pack('<d', new_value)
        self.replace_bytes(value_pos, new_value_bytes)

    def replace_array(self, array_name: str, property_type: str, new_items: List[bytes], position: int = None):
        if self.save_context is None:
            raise ValueError("Save context is not set")
        
        if position is not None:
            self.set_position(position)

        # remove array
        self.snip_bytes(8) # name
        self.snip_bytes(8) # ArrayProperty
        array_length = self.read_uint32()
        self.set_position(self.position - 4)
        self.snip_bytes(8) # length
        self.snip_bytes(8) # type
        self.snip_bytes(1) # end of struct
        self.snip_bytes(array_length) # array itself

        # insert new array if needed
        if new_items is None:
            return
        
        self.insert_array(array_name, property_type, new_items)
