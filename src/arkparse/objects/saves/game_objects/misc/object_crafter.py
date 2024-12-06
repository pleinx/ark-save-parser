from dataclasses import dataclass
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject

@dataclass
class ObjectCrafter:
    tribe_name: str #CrafterTribeName
    char_name: str #CrafterCharacterName

    def __init__(self, obj: ArkGameObject):
        self.tribe_name = obj.get_property_value("CrafterTribeName")
        self.char_name = obj.get_property_value("CrafterCharacterName")

    def __str__(self) -> str:
        tribe = self.tribe_name if self.tribe_name is not None else "Unknown"
        char_name = self.char_name if self.char_name is not None else "Unknown"

        return f"\"{char_name}\" of tribe \"{tribe}\""
    
    def __eq__(self, value : "ObjectCrafter") -> bool:
        return self.tribe_name == value.tribe_name and self.char_name == value.char_name