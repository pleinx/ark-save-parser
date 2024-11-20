# from arkparse.logging import ArkSaveLogger
# from arkparse.parsing.ark_binary_parser import ArkBinaryParser

# from typing import Dict
# import struct

# def check_string(byte_buffer, s):
#     read = byte_buffer.read_string()
#     if read != s:
#         ArkSaveLogger.open_hex_view()
#         raise Exception(f"Expected {hex(s)} but got {hex(read)}")


# def check_uint64(byte_buffer, u64):
#     read = byte_buffer.read_uint64()
#     if read != u64:
#         ArkSaveLogger.open_hex_view()
#         raise Exception(f"Expected {hex(u64)} but got {hex(read)}")


# def check_uint16(byte_buffer, u16):
#     read = byte_buffer.read_uint16()
#     if read != u16:
#         ArkSaveLogger.open_hex_view()
#         raise Exception(f"Expected {hex(u16)} but got {hex(read)}")


# def check_uint32(byte_buffer, u32):
#     read = byte_buffer.read_uint32()
#     if read != u32:
#         ArkSaveLogger.open_hex_view()
#         raise Exception(f"Expected {hex(u32)} but got {hex(read)}")


# def check_byte(byte_buffer, b):
#     read = byte_buffer.read_byte()
#     if read != b:
#         ArkSaveLogger.open_hex_view()
#         raise Exception(f"Expected {hex(b)} but got {hex(read)}")


# def check_save_name(byte_buffer, s):
#     read = byte_buffer.read_name()
#     if read != s:
#         ArkSaveLogger.open_hex_view()
#         raise Exception(f"Expected {hex(s)} but got {hex(read)}")


# def read_double(reader: ArkBinaryParser, property_name: str) -> float:
#     check_save_name(reader, property_name)
#     check_save_name(reader, "DoubleProperty")
#     check_byte(reader, 0x08)
#     check_uint64(reader, 0)
#     value = reader.read_double()
#     return value


# def read_boolean(reader: ArkBinaryParser, property_name: str) -> bool:
#     check_save_name(reader, property_name)
#     check_save_name(reader, "BoolProperty")
#     check_uint64(reader, 0)
#     value = reader.read_boolean()
#     return value


# def read_uint32(reader: ArkBinaryParser, property_name: str) -> int:
#     check_save_name(reader, property_name)
#     check_save_name(reader, "UInt32Property")
#     check_byte(reader, 0x04)
#     check_uint32(reader, 0)
#     value = reader.read_uint32()
#     return value


# def read_int32(reader: ArkBinaryParser, property_name: str) -> int:
#     check_save_name(reader, property_name)
#     check_save_name(reader, "IntProperty")
#     check_byte(reader, 0x04)
#     check_uint64(reader, 0)
#     value = reader.read_int()
#     return value


# def read_float(reader: ArkBinaryParser, property_name: str) -> float:
#     check_save_name(reader, property_name)
#     check_save_name(reader, "FloatProperty")
#     check_byte(reader, 0x04)
#     check_uint64(reader, 0)
#     value = reader.read_float()
#     return value


# def read_string(reader: ArkBinaryParser, property_name: str) -> str:
#     check_save_name(reader, property_name)
#     check_save_name(reader, "StrProperty")
#     reader.read_byte()  # length?
#     check_uint64(reader, 0)
#     value = reader.read_string()
#     return value


# def replace_string(reader: ArkBinaryParser, names: Dict[int, str], property_name: str, value: str):
#     original_position = reader.get_position()
#     property_position = reader.set_property_position(property_name, names)
#     reader.read_name()
#     reader.read_name()
#     reader.read_byte()  # length?
#     check_uint64(reader, 0)
#     current_string = reader.read_string()
#     current_nr_of_bytes = len(current_string) + 4
#     value_pos = property_position + 8 + 8 + 1 + 8
#     # length as 32 bit int
#     total_length_u32 = (current_nr_of_bytes +
#                         1).to_bytes(4, byteorder="little")
#     reader.replace_bytes(property_position + 8 + 8, total_length_u32)
#     lengthu32 = (len(value) + 1).to_bytes(4, byteorder="little")
#     reader.replace_bytes(value_pos, lengthu32 +
#                          value.encode("utf-8"), current_nr_of_bytes)
#     reader.set_position(original_position)
#     print(
#         f"Replaced string {current_string} (length={current_nr_of_bytes}) at {property_position} with {value} at {value_pos}")


# def replace_32_bit_int(reader: ArkBinaryParser, property_position: int, new_value: int):
#     value_pos = property_position + 8 + 8 + 1 + 8
#     new_value_bytes = new_value.to_bytes(4, byteorder="little")
#     reader.replace_bytes(value_pos, new_value_bytes)


# def replace_64_bit_int(reader: ArkBinaryParser, property_position: int, new_value: int):
#     value_pos = property_position + 8 + 8 + 1 + 8
#     new_value_bytes = new_value.to_bytes(8, byteorder="little")
#     reader.replace_bytes(value_pos, new_value_bytes)


# def replace_float(reader: ArkBinaryParser, property_position: int, new_value: float):
#     value_pos = property_position + 8 + 8 + 1 + 8
#     new_value_bytes = struct.pack('<f', new_value)
#     reader.replace_bytes(value_pos, new_value_bytes)


# def replace_double(reader: ArkBinaryParser, property_position: int, new_value: float):
#     value_pos = property_position + 8 + 8 + 1 + 8
#     new_value_bytes = struct.pack('<d', new_value)
#     reader.replace_bytes(value_pos, new_value_bytes)
