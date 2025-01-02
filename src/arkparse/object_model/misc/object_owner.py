from dataclasses import dataclass
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.logging import ArkSaveLogger

from arkparse.player.ark_player import ArkPlayer
from arkparse.ark_tribe import ArkTribe

@dataclass
class ObjectOwner:
    original_placer_id: int = None      #OriginalPlacerPlayerID
    tribe_name: str = None              #OwnerName (tribename)
    player_name: str = None             #OwningPlayerName
    id_: int = None                     #OwningPlayerID
    tribe_id: int = None                #TargetingTeam

    def __init__(self, properties: ArkPropertyContainer = None):
        if properties is None:
            return
        self.original_placer_id = properties.get_property_value("OriginalPlacerPlayerID")
        self.tribe_name = properties.get_property_value("OwnerName")
        self.player_name = properties.get_property_value("OwningPlayerName")
        self.id_ = properties.get_property_value("OwningPlayerID")
        self.tribe_id = properties.get_property_value("TargetingTeam")

    def set_in_binary(self, binary: ArkBinaryParser):
        ArkSaveLogger.set_file(binary, "debug.bin")

        if binary is not None:
            if self.original_placer_id is not None:
                binary.replace_u32(binary.set_property_position("OriginalPlacerPlayerID"), self.original_placer_id)
            if self.tribe_name is not None:
                binary.replace_string(binary.set_property_position("OwnerName"), self.tribe_name)
            if self.player_name is not None:
                binary.replace_string(binary.set_property_position("OwningPlayerName"), self.player_name)
            if self.id_ is not None:
                binary.replace_u32(binary.set_property_position("OwningPlayerID"), self.id_)
            if self.tribe_id is not None:
                binary.replace_u32(binary.set_property_position("TargetingTeam"), self.tribe_id)

        return binary

    def __str__(self) -> str:
        return f"\"{self.player_name}\" ({self.id_}) of tribe \"{self.tribe_name}\" ({self.tribe_id})"# (originally placed by {self.original_placer_id})"
    
    def set_tribe(self, tribe_id: int, tribe_name: str="None"):
        self.tribe_id = tribe_id
        self.tribe_name = tribe_name

    def set_player(self, player_id: int=0, player_name: str="None"):
        self.id_ = player_id
        self.player_name = player_name
        self.original_placer_id = player_id
    
    def replace_self_with(self, other: "ObjectOwner", binary: ArkBinaryParser = None):
        self.original_placer_id = None if self.original_placer_id is None else other.original_placer_id
        self.tribe_name = None if self.tribe_name is  None else other.tribe_name
        self.tribe_id = None if self.tribe_id is  None else other.tribe_id
        self.player_name = None if self.player_name is  None else other.player_name
        self.id_ = None if self.id_ is  None else other.id_

        if binary is not None:
            self.set_in_binary(binary)

    def serialize(self):
        return {
            "original_placer_id": self.original_placer_id,
            "tribe_name": self.tribe_name,
            "player_name": self.player_name,
            "id_": self.id_,
            "tribe_id": self.tribe_id
        }
    
    @staticmethod
    def from_profile(profile: ArkPlayer, tribe: ArkTribe):
        obj = ObjectOwner()
        obj.id_ = profile.id_
        obj.tribe_name = tribe.name
        obj.player_name = profile.name
        obj.original_placer_id = profile.id_
        obj.tribe_id = tribe.tribe_id

        return obj