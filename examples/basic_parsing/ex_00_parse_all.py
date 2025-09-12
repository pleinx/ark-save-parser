from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap

from arkparse.logging import ArkSaveLogger

ArkSaveLogger.allow_invalid_objects(False)

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
    save_path = ArkFtpClient.from_config(
        Path("../../ftp_config.json"), ArkMap.RAGNAROK).download_save_file(Path.cwd()) # or from FTP

    ArkSaveLogger.info_log("Starting to parse all game objects from the save file...")
    parsed_objects, _ = ex_00_parse_all(save_path)
    ArkSaveLogger.info_log(f"Finished parsing. Total objects parsed: {len(parsed_objects)}")



