from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from arkparse.struct.ark_rotator import ArkRotator
from arkparse.struct.ark_vector import ArkVector
from arkparse.struct.actor_transform import ActorTransform

from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing.ark_property_container import ArkPropertyContainer
from arkparse.objects.saves.save_context import SaveContext
from arkparse.logging import ArkSaveLogger

@dataclass
class ArkGameObject(ArkPropertyContainer):
    uuid: Optional[UUID] = None
    blueprint: Optional[str] = None
    location: Optional[ActorTransform] = None
    uuid2: str = ""

    def __init__(self, uuid: Optional[UUID] = None, blueprint: Optional[str] = None, binary_reader: Optional[ArkBinaryParser] = None):
        super().__init__()
        if binary_reader:
            self.uuid = uuid
            self.uuid2 = ""

            binary_reader.set_position(0)
            self.blueprint = binary_reader.read_name()
            
            sContext : SaveContext = binary_reader.save_context
            self.location = sContext.get_actor_transform(uuid) or None
            ArkSaveLogger.debug_log(f"Retrieved actor location: {('Success' if self.location else 'Failed')}")
            ArkSaveLogger.debug_log(f"Blueprint: {blueprint}")
            binary_reader.validate_uint32(0)

    @classmethod
    def read_from_custom_bytes(cls, reader: ArkBinaryParser) -> "ArkGameObject":
        ark_game_object = cls()
        ark_game_object.uuid = reader.read_uuid()
        ark_game_object.blueprint = reader.read_string()
        reader.validate_uint32(0)
        # ark_game_object.names = reader.read_strings_array()
        
        from_data_file = reader.read_boolean()  # Placeholder for unknown data
        data_file_index = reader.read_int()  # Placeholder for unknown data
        
        if reader.read_boolean():
            rotator = ArkRotator(reader)  # Placeholder for rotation data
            ark_game_object.location = ActorTransform(ArkVector(0, 0, 0), rotator)
        
        # ark_game_object.properties_offset = reader.read_int()
        reader.validate_uint32(0)

        return ark_game_object

    def read_extra_data(self, reader: ArkBinaryParser):
        if reader.has_more() and reader.read_boolean():
            self.uuid2 = reader.read_uuid()

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