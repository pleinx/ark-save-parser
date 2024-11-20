from arkparse.struct.struct_val_check import check_uint32, check_byte, check_save_name
from ....ark_binary_data import ArkBinaryParser
from ....ark_save_utils import ArkSaveLogger
from arkparse.struct.actor_transform import ActorTransform
from arkparse.objects.saves.game_objects import ArkGameObject

from uuid import UUID

class AutomatedDinoWipe(ArkGameObject):
    actor_location : ActorTransform
    creation_time : float
    uuid_maybe : UUID

    def __init__(self, uuid: UUID, buffer: ArkBinaryParser):
        debug_active = ArkSaveLogger.enable_debug
        ArkSaveLogger.enable_debug = False
        super().__init__(uuid, "/AutomatedDinoWipes/AutomatedDinoWipes_CCA.AutomatedDinoWipes_CCA_C", buffer)
        ArkSaveLogger.enable_debug = debug_active
        
        check_uint32(buffer, 1)
        self.name = buffer.read_string()
        check_uint32(buffer, 0)
        check_byte(buffer, 0x08)
        self.creation_time = self.read_double(buffer, "OriginalCreationTime")
        check_save_name(buffer, "None")
        check_uint32(buffer, 1)
        self.uuid = buffer.read_uuid()
        
        ArkSaveLogger.debug_log(f"Name: {self.name} - UUID: {self.uuid} - Creation Time: {self.creation_time}")
