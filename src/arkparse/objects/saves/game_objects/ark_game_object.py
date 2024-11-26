from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from arkparse.struct.ark_rotator import ArkRotator
from arkparse.parsing.ark_property import ArkProperty
from arkparse.struct.actor_transform import ActorTransform

from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing.ark_property_container import ArkPropertyContainer
from arkparse.objects.saves.save_context import SaveContext
from arkparse.logging import ArkSaveLogger

@dataclass
class ArkGameObject(ArkPropertyContainer):
    uuid: Optional[UUID] = None
    uuid2: str = ""

    blueprint: Optional[str] = None
    location: Optional[ActorTransform] = None

    names: List[str] = field(default_factory=list)
    section: Optional[str] = None
    unknown: Optional[int] = None
    properties_offset : int = 0

    def __init__(self, uuid: Optional[UUID] = None, blueprint: Optional[str] = None, binary_reader: Optional[ArkBinaryParser] = None, from_custom_bytes: bool = False, no_header: bool = False):
        super().__init__()
        if binary_reader:
            ArkSaveLogger.set_file(binary_reader, "debug.bin")
            if not no_header:
                if not from_custom_bytes:
                    self.uuid = uuid
                    self.uuid2 = ""
                    binary_reader.set_position(0)

                    self.blueprint = binary_reader.read_name()

                    sContext : SaveContext = binary_reader.save_context
                    self.location = sContext.get_actor_transform(uuid) or None
                    ArkSaveLogger.debug_log(f"Retrieved actor location: {('Success' if self.location else 'Failed')}")
                    
                else:
                    self.uuid = binary_reader.read_uuid()
                    self.blueprint = binary_reader.read_string()

                ArkSaveLogger.debug_log(f"Blueprint: {blueprint}")
                binary_reader.validate_uint32(0)

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
                    
            if no_header:
                self.blueprint = self.get_property_value("ItemArchetype").value
                    
    def read_props_at_offset(self, reader: ArkBinaryParser):
        reader.set_position(self.properties_offset)
        # if reader.position != self.properties_offset:
        #     ArkSaveLogger.open_hex_view()
        #     raise Exception("Invalid offset for properties: ", reader.position, "expected: ", self.properties_offset)
        self.read_properties(reader, ArkProperty, reader.size())
        # reader.read_int()
        # self.uuid2 = reader.read_uuid()

    def read_double(self, reader: ArkBinaryParser, property_name: str) -> float:
        reader.validate_name(property_name)
        reader.validate_name("DoubleProperty")
        reader.validate_byte(0x08)
        reader.validate_uint64(0)
        value = reader.read_double()
        return value
    
    def read_boolean(self, reader: ArkBinaryParser, property_name: str) -> bool:
        reader.validate_name(property_name)
        reader.validate_name("BoolProperty")
        reader.validate_uint64(0)
        value = reader.read_boolean()
        return value
    
    def decode_name(self, buffer: ArkBinaryParser):
        buffer.validate_uint32(1)
        name = buffer.read_string()
        buffer.validate_uint32(0)
        return name