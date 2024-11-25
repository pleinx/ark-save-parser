from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing.ark_property import ArkProperty
from arkparse.logging import ArkSaveLogger
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.struct.ark_rotator import ArkRotator

@dataclass
class AbstractGameObject(ArkGameObject):
    names: List[str] = field(default_factory=list)
    section: Optional[str] = None
    unknown: Optional[int] = None
    properties_offset : int = 0

    def __init__(self, uuid: Optional[UUID] = None, blueprint: Optional[str] = None, binary_reader: Optional[ArkBinaryParser] = None, from_custom_bytes: bool = False):
        super().__init__(uuid, blueprint, binary_reader,from_custom_bytes)
        if binary_reader:
            if not from_custom_bytes:
                self.names = binary_reader.read_names(binary_reader.read_int())
            else:
                self.names = binary_reader.read_strings_array()

            for name in self.names:
                ArkSaveLogger.debug_log(f"Name: {name}")

            self.section = binary_reader.read_part()
            self.unknown = binary_reader.read_byte()
            
            if from_custom_bytes:
                binary_reader.validate_uint16(0)
                binary_reader.validate_byte(0)
                has_rotator = binary_reader.read_uint32() == 1
                if has_rotator:
                    ArkRotator(binary_reader)  # Placeholder for rotation data

                self.properties_offset = binary_reader.read_uint32()
                binary_reader.validate_uint32(0)

            if not from_custom_bytes: 
                self.read_properties(binary_reader, ArkProperty, binary_reader.size())

                if  binary_reader.size() - binary_reader.position >= 20:
                    binary_reader.set_position(binary_reader.size() - 20)
                    binary_reader.read_int()
                    self.uuid2 = binary_reader.read_uuid()

                    if binary_reader.has_more():
                        ArkSaveLogger.enable_debug = True
                        ArkSaveLogger.open_hex_view()
                        raise Exception("Unknown data left")
                    
    def read_props_at_offset(self, reader: ArkBinaryParser):
        reader.set_position(self.properties_offset)
        # if reader.position != self.properties_offset:
        #     ArkSaveLogger.open_hex_view()
        #     raise Exception("Invalid offset for properties: ", reader.position, "expected: ", self.properties_offset)
        self.read_properties(reader, ArkProperty, reader.size())
        # reader.read_int()
        # self.uuid2 = reader.read_uuid()
