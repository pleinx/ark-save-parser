from ..ark_game_object import ArkGameObject
from uuid import UUID
from arkparse.parsing import ArkBinaryParser

class ParsedObjectBase:
    binary: ArkBinaryParser
    object: ArkGameObject

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