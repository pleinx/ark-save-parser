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
        self.tribe_id = obj.get_property_value("TamingTeamID")
        self.tamer_string = obj.get_property_value("TamerString")
        self.player = obj.get_property_value("OwningPlayerName")
        self.imprinter = obj.get_property_value("ImprinterName")
        self.imprinter_unique_id = obj.get_property_value("ImprinterPlayerUniqueNetId")
        self.id_ = obj.get_property_value("OwningPlayerID")

    # def set_in_save(self, binary: ArkBinaryParser):
    #     if self.original_placer_id is not None

    def __str__(self) -> str:
        tribe = self.tribe if self.tribe is not None else "Unknown"
        tribe_id = self.tribe_id if self.tribe_id is not None else -1

        tamer = self.tamer_string if self.tamer_string is not None else "Unknown"
        tamer_tribe_id = self.tamer_tribe_id if self.tamer_tribe_id is not None else -1

        imprinter = self.imprinter if self.imprinter is not None else "Unknown"
        imprinter_id = self.imprinter_unique_id if self.imprinter_unique_id is not None else -1

        player = self.player if self.player is not None else "Unknown"
        player_id = self.id_ if self.id_ is not None else -1

        return f"\"{player}\" ({player_id}) of tribe \"{tribe}\" ({tribe_id}), tamer: \"{tamer}\" ({tamer_tribe_id}), imprinter: \"{imprinter}\" ({imprinter_id})"
    
    def is_valid(self):
        return self.player is not None or self.id_ is not None or self.tribe is not None or self.tribe_id is not None or self.targeting_team is not None or self.tamer_string is not None or self.tamer_tribe_id is not None or self.imprinter is not None or self.imprinter_unique_id is not None