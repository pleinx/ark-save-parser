from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject

from arkparse.logging import ArkSaveLogger

def ex_00_parse_all(path: Path):
    """
    Example 00: Parse all game objects from a save file.
    This example demonstrates how to parse all game objects from a save file.
    """
    save = AsaSave(path)
    obj: Dict[UUID, ArkGameObject] = save.get_game_objects()

    return obj, save.faulty_objects

if __name__ == "__main__":
    save_path = Path.cwd() / "save.ark" # Change this to your save file path

    ArkSaveLogger.info_log("Starting to parse all game objects from the save file...")
    parsed_objects, _ = ex_00_parse_all(save_path)
    ArkSaveLogger.info_log(f"Finished parsing. Total objects parsed: {len(parsed_objects)}")



