from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import GameObjectReaderConfiguration

# retrieve the save file
save_path = Path.cwd() / "Ragnarok_WP.ark"
save = AsaSave(save_path)

config = GameObjectReaderConfiguration(
    property_names= [
        "TamerString",
        "Health"
    ]  # Create filter
)
# Create list of generic Ark objects
objects: Dict[UUID, ArkGameObject] = save.get_game_objects(config)

for obj in objects.values():
    print(obj.get_short_name())
