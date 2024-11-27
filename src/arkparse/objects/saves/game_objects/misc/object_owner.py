from dataclasses import dataclass
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.logging import ArkSaveLogger

@dataclass
class ObjectOwner:
    original_placer_id: int = None#OriginalPlacerPlayerID
    name: str = None#OwnerName (tribename)
    player_name: str = None#OwningPlayerName
    id_: int = None#OwningPlayerID

    def __init__(self, properties: ArkPropertyContainer = None):
        if properties is None:
            return
        self.original_placer_id = properties.get_property_value("OriginalPlacerPlayerID")
        self.name = properties.get_property_value("OwnerName")
        self.player_name = properties.get_property_value("OwningPlayerName")
        self.id_ = properties.get_property_value("OwningPlayerID")

    def set_in_binary(self, binary: ArkBinaryParser):
        ArkSaveLogger.set_file(binary, "debug.bin")

        if binary is not None:
            if self.original_placer_id is not None:
                binary.replace_u32(binary.set_property_position("OriginalPlacerPlayerID"), self.original_placer_id)
            if self.name is not None:
                binary.replace_string(binary.set_property_position("OwnerName"), self.name)
            if self.player_name is not None:
                binary.replace_string(binary.set_property_position("OwningPlayerName"), self.player_name)
            if self.id_ is not None:
                binary.replace_u32(binary.set_property_position("OwningPlayerID"), self.id_)

        return binary

    def __str__(self) -> str:
        return f"\"{self.player_name}\" ({self.id_}) of tribe \"{self.name}\""# (originally placed by {self.original_placer_id})"
    
    def replace_self_with(self, other: "ObjectOwner"):
        self.original_placer_id = None if self.original_placer_id is None else other.original_placer_id
        self.name = None if self.name is  None else other.name
        self.player_name = None if self.player_name is  None else other.player_name
        self.id_ = None if self.id_ is  None else other.id_
    
    @staticmethod
    def from_profile(id_: int, name: str, tribe_name: str):
        obj = ObjectOwner()
        obj.id_ = id_
        obj.name = tribe_name
        obj.player_name = name
        obj.original_placer_id = id_

        return obj