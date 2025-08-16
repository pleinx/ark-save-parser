import json
from time import time
from arkparse.api.dino_api import DinoApi, Dino
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from pprint import pprint
import argparse
from pathlib import Path
import os
import ast
from datetime import datetime
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

# HELPER FUNCTIONS
def extract_owner_attr(dino, dino_json_data, attr_name):
    val = getattr(dino.cryopod.dino.owner, attr_name, None) if dino.is_cryopodded else (
        getattr(dino.owner, attr_name, None) if dino.owner else None
    )
    return val if val else dino_json_data.get(attr_name, None)

def convert_tamed_time(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, "%Y.%m.%d-%H.%M.%S").strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def extract_added_stat_values(stat_string):
    if not stat_string:
        return {}

    key_map = {
        "health": "hp-a",
        "stamina": "stam-a",
        "melee_damage": "melee-a",
        "weight": "weight-a",   # TODO is missing always 0.0
        "movement_speed": "speed-a",
        "food": "food-a",
        "oxygen": "oxy-a"
    }

    matches = re.findall(r'(\w+)=([\d.]+)', stat_string)

    return {
        key_map[k]: v
        for k, v in matches
        if k in key_map
    }

def load_tamable_classnames(filepath: str) -> set:
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# Load ASA save
save_path = Path(f"{args.savegame}")
if not save_path.exists():
    raise FileNotFoundError(f"Save file not found at: {save_path}")

tamable_path = os.path.join(BASE_DIR, "..", "..", "wip", "classes", "uncategorized", "tamable_dinos.txt")
TAMABLE_CLASSNAMES = load_tamable_classnames(tamable_path)

save = AsaSave(save_path)

# Extract map name
map_folder = save_path.parent.name
# Extract map name from file
map_name = save_path.stem  # e.g 'Aberration_WP'

export_folder = Path(f"{args.output}/{map_folder}")
export_folder.mkdir(parents=True, exist_ok=True)
json_output_path = export_folder / f"{map_folder}_WildDinos.json"

dino_api = DinoApi(save)

# TODO: json format only on my machine

dinos = []
for dino_id, dino in dino_api.get_all_wild_tamables().items():
    if not isinstance(dino, Dino):
        continue

    dino_json_data = dino.to_json_obj()
    dino_class = dino.get_short_name() + "_C"
    lvl = dino.stats.base_level if dino.stats else None

    # Corrupt dinos are not tamable
    if "_Corrupt" in dino_class:
        continue

    # Bionic (TEK) dinos max level check
    if "Bionic" in dino_class and lvl > 180:
        continue

    # Non-TEK dinos max level check
    if "Bionic" not in dino_class and lvl > 150:
        continue

    lat, lon = (0.0, 0.0)
    ccc = ""
    if not dino.is_cryopodded and dino.location:
        ccc = f"{dino.location.x:.2f} {dino.location.y:.2f} {dino.location.z:.2f}"
        coords = dino.location.as_map_coords(MAP_NAME_MAPPING.get(map_name))
        if(coords):
            lat = coords.lat
            lon = coords.long

    # extract dino stats
    stats_entry = {}
    for prefix, field in STAT_NAME_MAP.items():
        stats_entry[f"{prefix}-w"] = getattr(dino.stats.base_stat_points, field, 0)
        stats_entry[f"{prefix}-t"] = getattr(dino.stats.added_stat_points, field, 0)
        stats_entry[f"{prefix}-m"] = getattr(dino.stats.mutated_stat_points, field, 0)

    entry = {
        "id": str(dino_id),
        "creature": dino_class,
        "sex": "Female" if dino.is_female else "Male",
        "lvl": lvl,
        "lat": lat,
        "lon": lon,
        "hp": stats_entry["hp-w"],
        "stam": stats_entry["stam-w"],
        "melee": stats_entry["melee-w"],
        "weight": stats_entry["weight-w"],
        "speed": stats_entry["speed-w"],
        "food": stats_entry["food-w"],
        "oxy": stats_entry["oxy-w"],
        "craft": stats_entry["craft-w"],
        "dinoid": str(dino_id),
        "tameable": "true",
        "trait": dino_json_data.get("GeneTraits", None) if dino_json_data.get("GeneTraits", None) else ""
    }

    # Adding Dino Colors
    color_indices_str = dino_json_data.get("ColorSetIndices", "[]")
    try:
        color_indices = ast.literal_eval(color_indices_str)
    except (ValueError, SyntaxError):
        color_indices = [None] * 6

    entry["c0"] = color_indices[0] if len(color_indices) > 0 else None
    entry["c1"] = color_indices[1] if len(color_indices) > 1 else None
    entry["c2"] = color_indices[2] if len(color_indices) > 2 else None
    entry["c3"] = color_indices[3] if len(color_indices) > 3 else None
    entry["c4"] = color_indices[4] if len(color_indices) > 4 else None
    entry["c5"] = color_indices[5] if len(color_indices) > 5 else None

    dinos.append(entry)

# CONTINUE WITH JSON EXPORT
json_data = {
    "map": map_folder,
    "data": dinos
}

if os.path.exists(json_output_path):
    os.remove(json_output_path)

with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, separators=(',', ':'))

# DONE, OUTPUT
print(f"Saved {len(dinos)} dinos to {json_output_path}")

elapsed = time() - start_time
print(f"Script runtime: {elapsed:.2f} seconds")