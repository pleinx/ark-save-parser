from dataclasses import dataclass

from arkparse.objects.player.ark_profile import ArkProfile
from arkparse.objects.tribe.ark_tribe import ArkTribe
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing.ark_binary_parser import ArkBinaryParser

@dataclass
class DinoOwner:
    tribe: str = None                   #TribeName
    tamer_tribe_id: int = None          #TamingTeamID
    tamer_string: str = None            #TamerString
    player: str = None                  #OwningPlayerName
    imprinter: str = None               #ImprinterName
    imprinter_unique_id: int = None     #ImprinterPlayerUniqueNetId (string)
    id_: int = None                     #OwningPlayerID
    target_team: int = None             #TargetingTeam

    def __init__(self, obj: ArkGameObject = None):
        if obj is None:
            return
        
        self.tribe = obj.get_property_value("TribeName")
        self.tamer_tribe_id = obj.get_property_value("TamingTeamID")
        self.tamer_string = obj.get_property_value("TamerString")
        self.player = obj.get_property_value("OwningPlayerName")
        self.imprinter = obj.get_property_value("ImprinterName")
        self.imprinter_unique_id = obj.get_property_value("ImprinterPlayerUniqueNetId")
        self.id_ = obj.get_property_value("OwningPlayerID")
        self.target_team = obj.get_property_value("TargetingTeam")

    # def set_in_save(self, binary: ArkBinaryParser):
    #     if self.original_placer_id is not None

    def set_in_binary(self, binary: ArkBinaryParser):
        if self.imprinter_unique_id is not None:
            binary.replace_string(binary.set_property_position("ImprinterPlayerUniqueNetId"), self.imprinter_unique_id)
        if self.id_ is not None:
            binary.replace_u32(binary.set_property_position("OwningPlayerID"), self.id_)
        if self.tribe is not None:
            binary.replace_string(binary.set_property_position("TribeName"), self.tribe)
        if self.tamer_tribe_id is not None:
            binary.replace_u32(binary.set_property_position("TamingTeamID"), self.tamer_tribe_id)
        if self.tamer_string is not None:
            binary.replace_string(binary.set_property_position("TamerString"), self.tamer_string)
        if self.player is not None:
            binary.replace_string(binary.set_property_position("OwningPlayerName"), self.player)
        if self.imprinter is not None:
            binary.replace_string(binary.set_property_position("ImprinterName"), self.imprinter)
        if self.target_team is not None:
            binary.replace_u32(binary.set_property_position("TargetingTeam"), self.target_team)

    def replace_with(self, other: "DinoOwner", binary: ArkBinaryParser = None):
        self.imprinter_unique_id = None if self.imprinter_unique_id is None else other.imprinter_unique_id
        self.imprinter = None if self.imprinter is None else other.imprinter
        self.player = None if self.player is None else other.player
        self.id_ = None if self.id_ is None else other.id_
        self.tribe = None if self.tribe is None else other.tribe
        self.tamer_tribe_id = None if self.tamer_tribe_id is None else other.tamer_tribe_id
        self.tamer_string = None if self.tamer_string is None else other.tamer_string
        self.target_team = None if self.target_team is None else other.target_team

        if binary is not None:
            self.set_in_binary(binary)

    @staticmethod
    def from_profile(tribe: ArkTribe, profile: ArkProfile):
        o = DinoOwner()
        o.imprinter_unique_id = profile.player_data.unique_id
        o.imprinter = profile.player_data.char_name
        o.player = profile.player_data.name
        o.id_ = profile.player_data.id_
        o.tribe = tribe.tribe_data.name
        o.tamer_tribe_id = tribe.tribe_data.tribe_id
        o.tamer_string = tribe.tribe_data.name
        o.target_team = tribe.tribe_data.tribe_id
        return o

    def __str__(self) -> str:
        out = "Dino owner("
        if self.player is not None:
            out += f"\"{self.player}\""
        
        if self.id_ is not None:
            out += f" ({self.id_})"

        if self.tribe is not None:
            out += f" of tribe \"{self.tribe}\""

        if len(out) > 11:
            out += ", "

        if self.tamer_string is not None or self.tamer_tribe_id is not None:
            out += "tamer:"

        if self.tamer_string is not None:
            out += f" \"{self.tamer_string}\""

        if self.tamer_tribe_id is not None:
            out += " (" if self.tamer_string is not None else " "
            out += f"{self.tamer_tribe_id}"
            out += ")" if self.tamer_string is not None else ""

        if len(out) > 11:
            out += ", "

        if self.imprinter is not None or self.imprinter_unique_id is not None:
            out += "imprinter:"

        if self.imprinter is not None:
            out += f" \"{self.imprinter}\""

        if self.imprinter_unique_id is not None:
            out += " (" if self.imprinter is not None else " "
            out += f"{self.imprinter_unique_id}"
            out += ")" if self.imprinter is not None else ""

        return out + ")"
    
    def is_valid(self):
        return self.player is not None or \
               self.id_ is not None or \
               self.tribe is not None or \
               self.tamer_string is not None or \
               self.tamer_tribe_id is not None or \
               self.imprinter is not None or \
               self.imprinter_unique_id is not None or \
               self.target_team is not None