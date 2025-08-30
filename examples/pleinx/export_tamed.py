from pprint import pprint
import re
import json
import os
import ast
import argparse
from pathlib import Path
from time import time
from datetime import datetime
from tempfile import NamedTemporaryFile

from arkparse.api.dino_api import DinoApi, TamedDino, TamedBaby
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.helpers.dino.is_wild_tamed import is_wild_tamed

start_time = time()

# ---------- CLI ----------
parser = argparse.ArgumentParser(description="Export ASA tamed dinos to JSON.")
parser.add_argument("--savegame", type=str, required=True, help="Pfad zur .ark (z.B. C:/.../Aberration_WP.ark)")
parser.add_argument("--output", type=str, required=True, help="Ausgabeverzeichnis")
args = parser.parse_args()

# ---------- CONSTANTS ----------
STAT_NAME_MAP = {
    "hp": "health",
    "stam": "stamina",
    "melee": "melee_damage",
    "weight": "weight",
    "speed": "movement_speed",
    "food": "food",
    "oxy": "oxygen",
    "craft": "crafting_speed",
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

ADDED_KEY_MAP = {
    "health": "hp-a",
    "stamina": "stam-a",
    "melee_damage": "melee-a",
    "weight": "weight-a",          # TODO: scheint oft 0.0
    "movement_speed": "speed-a",
    "food": "food-a",
    "oxygen": "oxy-a",
}

# ---------- HELPERS ----------
def safe_owner_field(dino, field: str):
    """
    Holt Owner-Feld robust – bevorzugt aktiven Dino, sonst Cryo, sonst None.
    """
    try:
        if not getattr(dino, "is_cryopodded", False) and getattr(dino, "owner", None):
            return getattr(dino.owner, field, None)
        cryo_owner = getattr(getattr(getattr(dino, "cryopod", None), "dino", None), "owner", None)
        return getattr(cryo_owner, field, None) if cryo_owner else None
    except Exception:
        return None

# TODO dinos in cryopod have no real coords, you need to grap them of the player inventory/structures inventory etc. not implemented right now
def safe_location(dino):
    """
    Gibt ein Location-Objekt zurück – entweder vom aktiven Dino oder aus dem Cryopod.
    """
    if not getattr(dino, "is_cryopodded", False) and getattr(dino, "location", None):
        return dino.location
    cryo_dino = getattr(getattr(dino, "cryopod", None), "dino", None)
    return getattr(cryo_dino, "location", None)

def convert_tamed_time(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, "%Y.%m.%d-%H.%M.%S").strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def extract_added_stat_values(stat_string: str):
    if not stat_string:
        return {}
    matches = dict((k, v) for k, v in re.findall(r'(\w+)=([\d.]+)', stat_string))
    # map nur die Felder, die wir kennen
    return {ADDED_KEY_MAP[src]: matches[src] for src in ADDED_KEY_MAP if src in matches}

def pad_colors(color_indices, length=6):
    # erwartet Liste/iterable, aber akzeptiert auch String-Input
    if isinstance(color_indices, str):
        try:
            color_indices = ast.literal_eval(color_indices)
        except (ValueError, SyntaxError):
            color_indices = []
    if not isinstance(color_indices, (list, tuple)):
        color_indices = []
    return list(color_indices[:length]) + [None] * max(0, length - len(color_indices))

# ---------- LOAD SAVE ----------
save_path = Path(args.savegame)
if not save_path.exists():
    raise FileNotFoundError(f"Save file not found: {save_path}")

save = AsaSave(save_path)

map_folder = save_path.parent.name
map_name = save_path.stem  # e.g. 'Aberration_WP'
ark_map = MAP_NAME_MAPPING.get(map_name)
if ark_map is None:
    raise ValueError(f"Unknown map name '{map_name}'. Known: {', '.join(MAP_NAME_MAPPING)}")

export_folder = Path(args.output) / map_folder
export_folder.mkdir(parents=True, exist_ok=True)
json_output_path = export_folder / f"{map_folder}_TamedDinos.json"

# ---------- PROCESS ----------
dino_api = DinoApi(save)
tamed_dinos = []

for dino_id, dino in dino_api.get_all_tamed().items():
    if not isinstance(dino, (TamedDino, TamedBaby)):
        continue

    dino_json = dino.to_json_obj()

    # Location & coords
    if not dino.is_cryopodded:
        loc = safe_location(dino)
        ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
        coords = loc.as_map_coords(ark_map)
        lat = getattr(coords, "lat", 0.0) if coords else 0.0
        lon = getattr(coords, "long", 0.0) if coords else 0.0
    else:
        ccc, lat, lon = "", 0.0, 0.0

    # Tribe / Tamer
    tribe_id = safe_owner_field(dino, "tamer_tribe_id")
    tamer_name = safe_owner_field(dino, "tamer_string")

    # Sonderfall: Baby claimed oder nachträglich gecryopoddet → TargetingTeam fallback
    if (tribe_id == 2000000000 and dino_json.get("TargetingTeam")) or tribe_id is None:
        tribe_id = dino_json.get("TargetingTeam")

    # Base/Added/Mutated Stats kompakt aufbauen
    stats_entry = {}
    for prefix, field in STAT_NAME_MAP.items():
        base = getattr(getattr(dino.stats, "base_stat_points", None), field, 0) if getattr(dino, "stats", None) else 0
        add = getattr(getattr(dino.stats, "added_stat_points", None), field, 0) if getattr(dino, "stats", None) else 0
        mut = getattr(getattr(dino.stats, "mutated_stat_points", None), field, 0) if getattr(dino, "stats", None) else 0
        stats_entry[f"{prefix}-w"] = base
        stats_entry[f"{prefix}-t"] = add
        stats_entry[f"{prefix}-m"] = mut

    # Farben (c0..c5)
    c0, c1, c2, c3, c4, c5 = pad_colors(dino_json.get("ColorSetIndices", "[]"))

    entry = {
        "id": str(dino_id),
        "tribeid": tribe_id,
        "tribe": dino_json.get("TribeName"),
        "tamer": tamer_name,
        "imprinter": safe_owner_field(dino, "imprinter"),
        "imprint": int(getattr(dino, "percentage_imprinted", 0)),
        "creature": f"{dino.get_short_name()}_C",
        "name": dino.tamed_name or "",
        "sex": "Female" if getattr(dino, "is_female", False) else "Male",
        "base": getattr(getattr(dino, "stats", None), "base_level", None),
        "lvl": getattr(getattr(dino, "stats", None), "current_level", None),
        "lat": lat,
        "lon": lon,
        "cryo": getattr(dino, "is_cryopodded", False),
        "ccc": ccc,
        "dinoid": str(dino_id),
        "isMating": False,   # TODO
        "isNeutered": False, # TODO
        "isClone": False,    # TODO
        "maturation": float(getattr(dino, "percentage_matured", 100.0)) if isinstance(dino, TamedBaby) else "100",
        "traits": [],        # TODO
        "inventory": [],     # TODO
        "is_wild_tamed": bool(is_wild_tamed(dino)),
        "tamedAtTime": convert_tamed_time(dino_json.get("TamedTimeStamp")),
        "mut-f": dino_json.get("RandomMutationsFemale"),
        "mut-m": dino_json.get("RandomMutationsMale"),
        "c0": c0, "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
    }

    # Stats (-w/-t/-m) hinzufügen
    entry.update(stats_entry)

    # Added Stat Values aus String anhängen (hp-a, stam-a, ...)
    stat_values = dino_json.get("StatValues", "")
    if stat_values:
        entry.update(extract_added_stat_values(stat_values))

    tamed_dinos.append(entry)

# ---------- WRITE JSON (atomar) ----------
payload = {"map": map_folder, "data": tamed_dinos}

with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(export_folder), suffix=".tmp") as tf:
    json.dump(payload, tf, ensure_ascii=False, separators=(",", ":"))
    tmp_name = tf.name

os.replace(tmp_name, json_output_path)

print(f"Saved {len(tamed_dinos)} tamed dinos to {json_output_path}")
print(f"Script runtime: {time() - start_time:.2f} seconds")