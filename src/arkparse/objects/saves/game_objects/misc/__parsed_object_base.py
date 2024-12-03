from ..ark_game_object import ArkGameObject
from uuid import UUID
from arkparse.parsing import ArkBinaryParser
from pathlib import Path

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

    def store_binary(self, path: Path):
        file_path = path / ("obj_" + str(self.object.uuid))
        with open(file_path, "wb") as file:
            file.write(self.binary.byte_buffer)

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