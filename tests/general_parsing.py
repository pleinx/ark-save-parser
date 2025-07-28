from pathlib import Path
from APExamples.basic_parsing.ex_00_parse_all import ex_00_parse_all

from arkparse.logging import ArkSaveLogger

BASE_PATH = Path("D:\\ARK servers\\Ascended\\arkparse\\APExamples\\temp\\ASV")

def get_save_path(map_name: str) -> Path:
    """
    Get the path to the save file for a given map name.
    """

    return BASE_PATH / f"{map_name}_WP" / f"{map_name}_WP.ark"

MAPS = [
    "Extinction",
    "Aberration",
    "Astraeos",
    "Ragnarok",
    "TheIsland",
    "TheCenter",
    "ScorchedEarth",
]

if __name__ == "__main__":
    ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.SAVE, False)
    for map_name in MAPS:
        ArkSaveLogger.info_log(f"Parsing map: {map_name}, please wait...")
        save_path = get_save_path(map_name)
        objects, faulty_objects = ex_00_parse_all(save_path)
        ArkSaveLogger.info_log(f"Map: {map_name}, Parsed Objects: {len(objects)}, Faulty Objects: {faulty_objects}")