from dataclasses import dataclass
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ObjectReference:
    TYPE_ID = 0
    TYPE_PATH = 1
    TYPE_PATH_NO_TYPE = 2
    TYPE_NAME = 3
    TYPE_UUID = 4
    TYPE_POS_MOD_REF = 5
    TYPE_UNKNOWN = -1

    type: int
    value: any

    def __init__(self, reader: "ArkBinaryParser" = None):
        if reader is None:
            self.value = None
            return

        # If the save context has a name table, handle accordingly
        if reader.save_context.has_name_table():
            is_name = reader.read_short() == 1
            if is_name:
                self.type = ObjectReference.TYPE_PATH
                self.value = reader.read_name()
            else:
                self.type = ObjectReference.TYPE_UUID
                self.value = reader.read_uuid_as_string()
            return

        # Handle object types
        object_type = reader.read_int()
        if object_type == -1:
            self.type = ObjectReference.TYPE_UNKNOWN
            raise ValueError("Unknown object type encountered in ObjectReference")
        elif object_type == 0:
            self.type = ObjectReference.TYPE_ID
            self.value = reader.read_int()
        elif object_type == 1:
            self.type = ObjectReference.TYPE_PATH
            self.value = reader.read_string()
        else:
            reader.skip_bytes(-4)
            self.type = ObjectReference.TYPE_PATH_NO_TYPE
            self.value = reader.read_string()

def get_uuid_reference_bytes(uuid: UUID) -> bytes:
    bytes_ = bytearray()
    bytes_.extend(0x0000.to_bytes(2, byteorder="little"))
    bytes_.extend(uuid.bytes)
    return bytes_
    
