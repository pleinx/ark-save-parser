from arkparse.struct.struct_val_check import check_uint32, check_byte, check_save_name
from arkparse.parsing import ArkBinaryParser
from arkparse.logging import ArkSaveLogger
from arkparse.struct.actor_transform import ActorTransform
from arkparse.objects.saves.game_objects import ArkGameObject

from uuid import UUID

class RockWellArenaManager(ArkGameObject):
    actor_location : ActorTransform
    uuid_maybe : UUID

    def __init__(self, uuid: UUID, buffer: ArkBinaryParser):
        debug_active = ArkSaveLogger.enable_debug
        ArkSaveLogger.enable_debug = False
        super().__init__(uuid, "/Game/Aberration/Boss/Rockwell/BossArenaManager_Rockwell.BossArenaManager_Rockwell_C", buffer)
        ArkSaveLogger.enable_debug = debug_active
        check_uint32(buffer, 1)
        self.name = buffer.read_string()
        
        check_uint32(buffer, 0)
        check_byte(buffer, 0x0A)
        check_save_name(buffer, "None")
        check_uint32(buffer, 1)
        self.uuid = buffer.read_uuid()
        
        ArkSaveLogger.debug_log(f"Name: {self.name} - UUID: {self.uuid}")
