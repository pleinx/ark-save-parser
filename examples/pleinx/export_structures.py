from uuid import UUID
import json
from time import time
from arkparse.api import StructureApi
from arkparse.enums import ArkMap, ArkStat
from arkparse.saves.asa_save import AsaSave
from arkparse.api.player_api import PlayerApi
from pprint import pprint
import argparse
from pathlib import Path
import os
import ast
from datetime import datetime, timedelta
import re

start_time = time()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Args
parser = argparse.ArgumentParser(description="")
parser.add_argument("--savegame", type=str, required=True, help="MapName e.g. Aberration_WP")
parser.add_argument("--output", type=str, required=True, help="MapName e.g. Aberration_WP")
args = parser.parse_args()

# Mapping for custom JSON stat keys
STAT_NAME_MAP = {
    "hp": "health",
    "stam": "stamina",
    "melee": "melee_damage",
    "weight": "weight",
    "speed": "movement_speed",
    "food": "food",
    "oxy": "oxygen",
    "craft": "crafting_speed"
}

MAP_NAME_MAPPING = {
    "Aberration_WP": ArkMap.ABERRATION,
    "Extinction_WP": ArkMap.EXTINCTION,
    "TheIsland_WP": ArkMap.THE_ISLAND,
    "Ragnarok_WP": ArkMap.RAGNAROK,
    "ScorchedEarth_WP": ArkMap.SCORCHED_EARTH,
    "TheCenter_WP": ArkMap.THE_CENTER,
    "Astraeos_WP": ArkMap.ASTRAEOS,
}

# Load ASA save
save_path = Path(f"{args.savegame}")
if not save_path.exists():
    raise FileNotFoundError(f"Save file not found at: {save_path}")

save = AsaSave(save_path)

# Extract map name
map_folder = save_path.parent.name
# Extract map name from file
map_name = save_path.stem  # e.g 'Aberration_WP'

export_folder = Path(f"{args.output}/{map_folder}")
export_folder.mkdir(parents=True, exist_ok=True)
json_output_path = export_folder / f"{map_folder}_Structures.json"
structure_api = StructureApi(save)


def get_property_value(structure_json, property_name, default=None):
    return next(
        (prop.get("value") for prop in structure_json.get("properties", []) if prop.get("name") == property_name),
        default
    )

def get_base_name(name: str) -> str:
    return "_".join(name.split("_")[:-1])


jsonData = []
ctn=0
for structure in structure_api.get_all().values():
    owner_name = structure.object.get_property_value("OwnerName")
    if(owner_name == None):
        continue

    placed_ts = structure.object.get_property_value("OriginalPlacedTimeStamp", 0)
    if placed_ts:
        placed_ts = datetime.strptime(placed_ts, "%Y.%m.%d-%H.%M.%S")
        created = placed_ts.strftime("%Y-%m-%d %H:%M:%S")
    else:
        created = None

    lat, lon = (0.0, 0.0)
    ccc = ""
    if structure.location:
        ccc = f"{structure.location.x:.2f} {structure.location.y:.2f} {structure.location.z:.2f}"
        coords = structure.location.as_map_coords(MAP_NAME_MAPPING.get(map_name))
        if(coords):
            lat = coords.lat
            lon = coords.long

    entry = {
        "tribeid": structure.object.get_property_value("TargetingTeam"),
        "tribe": owner_name,
        "struct": structure.get_short_name() + "_C",
        "name": structure.object.get_property_value("BoxName"),
        "lat": lat,
        "lon": lon,
        "ccc": ccc,
        "created":  created,
        "inventory": []
    }

    jsonData.append(entry)


# CONTINUE WITH JSON EXPORT
json_data = {
    "map": map_folder,
    "data": jsonData
}

if os.path.exists(json_output_path):
    os.remove(json_output_path)

with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, separators=(',', ':'))

# DONE, OUTPUT
print(f"Saved {len(jsonData)} data to {json_output_path}")

elapsed = time() - start_time
print(f"Script runtime: {elapsed:.2f} seconds")


# Expected Output
#     {
#       "tribeid": 713052979,
#       "tribe": "Tribe of M0ix",
#       "struct": "StructureBP_Roof_Corner_Right_Inverted_Wood_C",
#       "name": "",
#       "lat": 60.857887,
#       "lon": 58.53211,
#       "ccc": "68256,87 86863,1 -20322,7",
#       "created": "19.03.2025 12:09:57",
#       "inventory": []
#     },