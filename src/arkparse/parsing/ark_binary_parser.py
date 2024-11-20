from typing import List, Dict
from uuid import UUID


from arkparse.struct.actor_transform import ActorTransform
from arkparse.logging import ArkSaveLogger
from ._property_parser import PropertyParser
from ._property_replacer import PropertyReplacer
from .ark_value_type import ArkValueType

class ArkBinaryParser(PropertyParser, PropertyReplacer):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)
    
    def read_value_type_by_name(self):
        position = self.get_position()
        key_type_name = self.read_name()
        key_type = ArkValueType.from_name(key_type_name)
        if key_type is None:
            ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()
            raise ValueError(f"Unknown value type {key_type_name} at position {position}")
        return key_type

    def read_actor_transforms(self) -> Dict[UUID, ActorTransform]:
        actor_transforms = {}
        termination_uuid = UUID("00000000-0000-0000-0000-000000000000")
        uuid = self.read_uuid()

        while uuid != termination_uuid:
            actor_transforms[uuid] = ActorTransform(self)
            uuid = self.read_uuid()

        return actor_transforms

    def read_part(self) -> str:
        part_index = self.read_int()
        if 0 <= part_index < len(self.save_context.parts):
            return self.save_context.parts[part_index]
        return None

    def read_uuids(self) -> List[UUID]:
        uuid_count = self.read_int()
        return [self.read_uuid() for _ in range(uuid_count)]
    
    def find_names(self):
        if not self.save_context.has_name_table():
            return []
        
        original_position = self.get_position()
        max_prints = 75
        prints = 0

        ArkSaveLogger.debug_log("--- Looking for names ---")
        found = {}
        for i in range(self.size() - 4):
            self.set_position(i)
            int_value = self.read_uint32()
            name = self.save_context.get_name(int_value)
            
            if name is not None:
                found[int_value] = name
                self.set_position(i)
                if prints < max_prints:
                    ArkSaveLogger.debug_log(f"Found name: {name} at {self.read_bytes_as_hex(4)} (position {i})")
                    prints += 1
                i += 3  # Adjust index to avoid overlapping reads
        self.set_position(original_position)
        return found
    
    def find_byte_sequence(self, bytes: bytes):
        original_position = self.get_position()
        max_prints = 75
        prints = 0

        ArkSaveLogger.debug_log("--- Looking for byte sequence ---")
        found = []
        for i in range(self.size() - len(bytes)):
            self.set_position(i)
            if self.read_bytes(len(bytes)) == bytes:
                found.append(i)
                self.set_position(i)
                if prints < max_prints:
                    ArkSaveLogger.debug_log(f"Found byte sequence at {self.read_bytes_as_hex(len(bytes))} (position {i})")
                    prints += 1
        self.set_position(original_position)
        return found
    
    
