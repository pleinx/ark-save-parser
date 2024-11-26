from dataclasses import dataclass
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject

@dataclass
class DinoOwner:
    tribe: str #TribeName
    tamer_tribe_id: int #TamingTeamID
    tamer_string: str #TamerString
    player: str #OwningPlayerName
    imprinter: str #ImprinterName
    imprinter_unique_id: int #ImprinterPlayerUniqueNetId
    id_: int #OwningPlayerID

    def __init__(self, obj: ArkGameObject):
        self.tribe = obj.get_property_value("TribeName")
        self.tamer_tribe_id = obj.get_property_value("TamingTeamID")
        self.tamer_string = obj.get_property_value("TamerString")
        self.player = obj.get_property_value("OwningPlayerName")
        self.imprinter = obj.get_property_value("ImprinterName")
        self.imprinter_unique_id = obj.get_property_value("ImprinterPlayerUniqueNetId")
        self.id_ = obj.get_property_value("OwningPlayerID")

    # def set_in_save(self, binary: ArkBinaryParser):
    #     if self.original_placer_id is not None

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
               self.imprinter_unique_id is not None