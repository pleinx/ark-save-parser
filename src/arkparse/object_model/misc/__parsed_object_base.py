from ..ark_game_object import ArkGameObject
from uuid import UUID, uuid4
from arkparse.parsing import ArkBinaryParser
from pathlib import Path
from arkparse.logging import ArkSaveLogger

from arkparse.saves.asa_save import AsaSave

class ParsedObjectBase:
    binary: ArkBinaryParser = None
    object: ArkGameObject = None

    def __get_class_name(self):
        self.binary.set_position(0)
        self.binary.read_name()

    def __init_props__(self, obj: ArkGameObject):
        self.object = obj

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        if binary is not None:
            self.binary = binary
            bp = self.__get_class_name()
            self.__init_props__(ArkGameObject(uuid=uuid, blueprint=bp, binary_reader=binary))

    def reidentify(self, new_uuid: UUID = None):
        self.replace_uuid(new_uuid=new_uuid)
        self.renumber_name()

    def replace_uuid(self, new_uuid: UUID = None, uuid_to_replace: UUID = None):
        if new_uuid is  None:
            new_uuid = uuid4()
        
        uuid_as_bytes = new_uuid.bytes
        ArkSaveLogger.debug_log(f"Replacing UUID {self.object.uuid} with {new_uuid}")
        ArkSaveLogger.debug_log(f"UUID bytes: {[hex(b) for b in uuid_as_bytes]}")
        ArkSaveLogger.debug_log(f"Old UUID bytes: {[hex(b) for b in self.object.uuid.bytes]}")
           
        old_uuid_bytes = self.object.uuid.bytes if uuid_to_replace is None else uuid_to_replace.bytes

        # Replace old UUID bytes with new UUID bytes
        self.binary.byte_buffer = self.binary.byte_buffer.replace(old_uuid_bytes, uuid_as_bytes)

        if uuid_to_replace is None:
            self.object.uuid = new_uuid

    def renumber_name(self):
        self.object.re_number_names(self.binary)

    def store_binary(self, path: Path, overwrite_path: bool = False):
        if overwrite_path:
            file_path = path
        else:
            file_path = path / ("obj_" + str(self.object.uuid) + ".bin")
        with open(file_path, "wb") as file:
            file.write(self.binary.byte_buffer)

    def update_binary(self, save: AsaSave):
        if save is not None:
            save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)

    def get_short_name(self):
        to_strip_end = [
            "_C",
        ]

        to_strip_start = [
            "PrimalItemResource_",
            "PrimalItemAmmo_",
        ]

        short = self.object.blueprint.split('/')[-1].split('.')[0]

        for strip in to_strip_end:
            if short.endswith(strip):
                short = short[:-len(strip)]

        for strip in to_strip_start:
            if short.startswith(strip):
                short = short[len(strip):]

        return short