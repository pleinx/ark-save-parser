from uuid import UUID
import json

from arkparse.api.dino_api import DinoApi, TamedDino
from arkparse.enums import ArkMap, ArkStat
from arkparse.saves.asa_save import AsaSave
from arkparse.api.player_api import PlayerApi
from pprint import pprint
import argparse
from pathlib import Path
import os
import ast
from datetime import datetime

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
    "CrystalIsles_WP": ArkMap.CRYSTAL_ISLES,
    "Extinction_WP": ArkMap.EXTINCTION,
    "Genesis_WP": ArkMap.GENESIS,
    "TheIsland_WP": ArkMap.ISLAND,
    "Ragnarok_WP": ArkMap.RAGNAROK,
    "ScorchedEarth_WP": ArkMap.SCORCHED_EARTH,
    "Valguero_WP": ArkMap.VALGUERO,
    "TheCenter_WP": ArkMap.ABERRATION,
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
json_output_path = export_folder / f"{map_folder}_TamedDinos.json"

dino_api = DinoApi(save)
player_api = PlayerApi(save)
tribe_lookup = {tribe.tribe_id: tribe.name for tribe in player_api.tribes}

tamed_dinos = []

for dino_id, dino in dino_api.get_all_filtered(tamed=True).items():
    if not isinstance(dino, TamedDino):
        continue

    dino_json_data = dino.to_json_obj()

    # public_attrs = [attr for attr in dir(dino.stats) if not attr.startswith('_')]
    # if(public_attrs is not []):
        # pprint(public_attrs)
        # coords = dino.location.as_map_coords(ArkMap.ABERRATION)
        # pprint(dir(coords))

#     if(dino_id=="26a06cb2-3cc3-e149-aaf5-1e28cdabdc51"):
#         public_attrs = [attr for attr in dir(dino.owner) if not attr.startswith('_')]
#         if(public_attrs is not []):
#             pprint(public_attrs)

    creature_name = dino.get_short_name()

    lat, lon = (0.0, 0.0)
    ccc = ""
    if not dino.is_cryopodded and dino.location:
        coords = dino.location.as_map_coords(MAP_NAME_MAPPING.get(map_name))
        if(coords):
            lat = coords.lat
            lon = coords.long

        ccc = f"{dino.location.x:.2f} {dino.location.y:.2f} {dino.location.z:.2f}"

    tribe_id = dino.cryopod.dino.owner.tamer_tribe_id if dino.is_cryopodded else (
        dino.owner.tamer_tribe_id if dino.owner else None
    )

    tribe_name = tribe_lookup.get(tribe_id, None)

    tamer_name = dino.cryopod.dino.owner.tamer_string if dino.is_cryopodded else (
        dino.owner.tamer_string if dino.owner else None
    )

    imprinter_name = dino.cryopod.dino.owner.imprinter if dino.is_cryopodded else (
        dino.owner.imprinter if dino.owner else None
    )

    if not tribe_name:
        tribe_name = dino_json_data.get("TribeName", None)

    if not imprinter_name:
        imprinter_name = dino_json_data.get("ImprinterName", None)

    tamed_at_str = dino_json_data.get("TamedTimeStamp", None)
    tamed_at_mysql = None

    if tamed_at_str:
        try:
            dt = datetime.strptime(tamed_at_str, "%Y.%m.%d-%H.%M.%S")
            tamed_at_mysql = dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            tamed_at_mysql = None

    # Extract stats
    stats_entry = {}
    for prefix, field in STAT_NAME_MAP.items():
        stats_entry[f"{prefix}-w"] = getattr(dino.stats.base_stat_points, field, 0)
        stats_entry[f"{prefix}-t"] = getattr(dino.stats.added_stat_points, field, 0)
        stats_entry[f"{prefix}-m"] = getattr(dino.stats.mutated_stat_points, field, 0)

    entry = {
        "id": str(dino_id),
        "tribeid": tribe_id,
        "tribe": tribe_name,  # TODO check why tribe name is often empty
        "tamer": tamer_name,
        "imprinter": imprinter_name,
        "imprint": 0.0,     # TODO
        "creature": creature_name,
        "name": dino.tamed_name if dino.tamed_name else "",
        "sex": "Female" if dino.is_female else "Male",
        "base": dino.stats.base_level if dino.stats else None,
        "lvl": dino.stats.current_level if dino.stats else None,
        "lat": lat,
        "lon": lon,
        "hp-w": stats_entry["hp-w"],
        "stam-w": stats_entry["stam-w"],
        "melee-w": stats_entry["melee-w"],
        "weight-w": stats_entry["weight-w"],
        "speed-w": stats_entry["speed-w"],
        "food-w": stats_entry["food-w"],
        "oxy-w": stats_entry["oxy-w"],
        "craft-w": stats_entry["craft-w"],
        "hp-m": stats_entry["hp-m"],
        "stam-m": stats_entry["stam-m"],
        "melee-m": stats_entry["melee-m"],
        "weight-m": stats_entry["weight-m"],
        "speed-m": stats_entry["speed-m"],
        "food-m": stats_entry["food-m"],
        "oxy-m": stats_entry["oxy-m"],
        "craft-m": stats_entry["craft-m"],
        "hp-t": stats_entry["hp-t"],
        "stam-t": stats_entry["stam-t"],
        "melee-t": stats_entry["melee-t"],
        "weight-t": stats_entry["weight-t"],
        "speed-t": stats_entry["speed-t"],
        "food-t": stats_entry["food-t"],
        "oxy-t": stats_entry["oxy-t"],
        "craft-t": stats_entry["craft-t"],
        "mut-f": dino_json_data.get("RandomMutationsFemale", None),
        "mut-m": dino_json_data.get("RandomMutationsMale", None),
        "cryo": dino.is_cryopodded,
        "ccc": ccc,
        "dinoid": str(dino_id),
        "isMating": False,          # TODO
        "isNeutered": False,        # TODO
        "isClone": False,           # TODO
        "tamedServer": dino.get_uploaded_from_server_name(),      # TODO
        "uploadedServer": dino.get_uploaded_from_server_name(),
        "maturation": "100",        # TODO
        "traits": [],               # TODO
        "inventory": [],            # TODO
        "tamedAtTime": tamed_at_mysql
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

    tamed_dinos.append(entry)

# EXPORT
json_data = {
    "map": map_folder,
    "data": tamed_dinos
}

if os.path.exists(json_output_path):
    os.remove(json_output_path)

with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print(f"Saved {len(tamed_dinos)} tamed dinos to {json_output_path}")