from dataclasses import dataclass
from arkparse.parsing import ArkBinaryParser
from arkparse.parsing import ArkPropertyContainer

@dataclass
class ObjectOwner:
    original_placer_id: int #OriginalPlacerPlayerID
    name: str #OwnerName
    player_name: str #OwningPlayerName
    id_: int #OwningPlayerID

    def __init__(self, properties: ArkPropertyContainer):
        self.original_placer_id = properties.get_property_value("OriginalPlacerPlayerID")
        self.name = properties.get_property_value("OwnerName")
        self.player_name = properties.get_property_value("OwningPlayerName")
        self.id_ = properties.get_property_value("OwningPlayerID")

    # def set_in_save(self, binary: ArkBinaryParser):
    #     if self.original_placer_id is not None

    def __str__(self) -> str:
        return f"\"{self.player_name}\" ({self.id_}) of tribe \"{self.name}\""# (originally placed by {self.original_placer_id})"