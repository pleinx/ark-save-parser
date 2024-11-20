from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing.ark_property import ArkProperty
from arkparse.logging import ArkSaveLogger
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject

@dataclass
class AbstractGameObject(ArkGameObject):
    names: List[str] = field(default_factory=list)
    section: Optional[str] = None
    unknown: Optional[int] = None
    properties_offset: int = field(default=0, repr=False)

    def __init__(self, uuid: Optional[UUID] = None, blueprint: Optional[str] = None, binary_reader: Optional[ArkBinaryParser] = None):
        super().__init__(uuid, blueprint, binary_reader)
        if binary_reader:
            self.names = binary_reader.read_names(binary_reader.read_int())
            for name in self.names:
                ArkSaveLogger.debug_log(f"Name: {name}")
            self.section = binary_reader.read_part()
            ArkSaveLogger.debug_log(f"Section: {self.section}")
            self.unknown = binary_reader.read_byte()

            self.read_properties(binary_reader, ArkProperty, binary_reader.size())

            if  binary_reader.size() - binary_reader.position >= 20:
                binary_reader.set_position(binary_reader.size() - 20)
                binary_reader.read_int()
                self.uuid2 = binary_reader.read_uuid()

                if binary_reader.has_more():
                    ArkSaveLogger.enable_debug = True
                    ArkSaveLogger.open_hex_view()
                    raise Exception("Unknown data left")
                

    # @classmethod
    # def read_from_custom_bytes(cls, reader: ArkBinaryParser) -> "ArkGameObject":
    #     ark_game_object = cls()
    #     ark_game_object.uuid = reader.read_uuid()
    #     ark_game_object.blueprint = reader.read_string()
    #     reader.expect(0, reader.read_int())
    #     ark_game_object.names = reader.read_strings_array()
        
    #     from_data_file = reader.read_boolean()  # Placeholder for unknown data
    #     data_file_index = reader.read_int()  # Placeholder for unknown data
        
    #     if reader.read_boolean():
    #         rotator = ArkRotator(reader)  # Placeholder for rotation data
    #         ark_game_object.location = ActorTransform(ArkVector(0, 0, 0), rotator)
        
    #     ark_game_object.properties_offset = reader.read_int()
    #     reader.expect(0, reader.read_int())

    #     return ark_game_object

    # def read_extra_data(self, reader: ArkBinaryParser):
    #     if reader.has_more() and reader.read_boolean():
    #         self.uuid2 = reader.read_uuid()
