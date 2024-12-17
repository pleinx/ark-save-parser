from arkparse.parsing.struct.struct_val_check import check_uint32, check_byte, check_save_name, check_uint64
from ....ark_binary_data import ArkBinaryParser
from ....ark_save_utils import ArkSaveLogger
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.object_model import ArkGameObject

from uuid import UUID

class NpcZoneManager(ArkGameObject):
    actor_location : ActorTransform
    linked_dinos: int
    directly_linked_dinos_present: bool
    uuid_maybe : UUID

    def __init__(self, uuid: UUID, buffer: ArkBinaryParser):
        super().__init__(uuid, "/Script/ShooterGame.NPCZoneManager", buffer)
        check_uint32(buffer, 1)
        self.name = buffer.read_string()
        
        check_uint32(buffer, 0)
        check_byte(buffer, 0x02)
        
        pos = buffer.get_position()
        name = buffer.read_name()

        if name == "bDirectlyLinkDinoCount":
            buffer.set_position(pos)
            self.directly_linked_dinos_present = self.read_boolean(buffer, "bDirectlyLinkDinoCount")
            check_save_name(buffer, "None")
        elif name == "None":
            self.directly_linked_dinos_present = False
        else:
            raise Exception(f"Unexpected name: {name}")
            
        check_uint32(buffer, 1)
        self.uuid = buffer.read_uuid()
        
        ArkSaveLogger.debug_log(f"Name: {self.name} - UUID: {self.uuid} - Directly Linked Dinos Present: {self.directly_linked_dinos_present}")
