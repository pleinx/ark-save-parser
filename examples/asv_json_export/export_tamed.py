#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Export ASA **tamed** dinos to JSON
# Output path requirement:
#   <output>/<serverkey>/TamedDinos.json
# Example:
#   python export_tamed.py --serverkey="extinction_a" \
#       --savegame="../temp/extinction_a/.../Extinction_WP.ark" \
#       --output=../output
#   => ../output/extinction_a/TamedDinos.json

import re
import json
import os
import ast
import argparse
from pathlib import Path
from time import time
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Optional, Tuple

from arkparse.api.dino_api import DinoApi, TamedDino, TamedBaby
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.helpers.dino.is_wild_tamed import is_wild_tamed

start_time = time()

# ---------- CLI ----------
parser = argparse.ArgumentParser(description="Export ASA tamed dinos to JSON.")
parser.add_argument("--savegame", type=Path, required=True, help="Path to .ark savegame file")
parser.add_argument("--output", type=Path, required=True, help="Base output directory. Final JSON will be <output>/<serverkey>/TamedDinos.json")
parser.add_argument("--serverkey", type=str, required=True, help="Server key used to build output folder name (e.g. extinction_a)")
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
    "weight": "weight-a",
    "movement_speed": "speed-a",
    "food": "food-a",
    "oxygen": "oxy-a",
}

# ---------- HELPERS ----------
def safe_owner_field(dino: Any, field: str) -> Optional[Any]:
    """Return an owner field safely, preferring active dino over cryo."""
    try:
        if not getattr(dino, "is_cryopodded", False) and getattr(dino, "owner", None):
            return getattr(dino.owner, field, None)
        cryo_owner = getattr(getattr(getattr(dino, "cryopod", None), "dino", None), "owner", None)
        return getattr(cryo_owner, field, None) if cryo_owner else None
    except Exception:
        return None


def safe_location(dino: Any) -> Optional[Any]:
    """Return a location object from active dino or cryo dino if available."""
    if not getattr(dino, "is_cryopodded", False) and getattr(dino, "location", None):
        return dino.location
    cryo_dino = getattr(getattr(dino, "cryopod", None), "dino", None)
    return getattr(cryo_dino, "location", None)


def convert_tamed_time(timestamp_str: Optional[str]) -> Optional[str]:
    """Convert 'YYYY.MM.DD-HH.MM.SS' into MySQL datetime 'YYYY-MM-DD HH:MM:SS'."""
    if not timestamp_str:
        return None
    try:
        dt = datetime.strptime(timestamp_str, "%Y.%m.%d-%H.%M.%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def extract_added_stat_values(stat_string: str) -> Dict[str, int]:
    """Extract added stat values from 'k=v' pairs into numeric dict using ADDED_KEY_MAP."""
    if not stat_string:
        return {}
    matches = dict((k, v) for k, v in re.findall(r"(\w+)=([\d.]+)", stat_string))
    result: Dict[str, int] = {}
    for src_key, dst_key in ADDED_KEY_MAP.items():
        if src_key in matches:
            try:
                num = float(matches[src_key])
                result[dst_key] = int(num) if num.is_integer() else int(round(num))
            except ValueError:
                continue
    return result


def pad_colors(color_indices: Any, length: int = 6) -> List[Optional[int]]:
    """Parse color indices from list/str and pad to fixed length with None."""
    if isinstance(color_indices, str):
        try:
            color_indices = ast.literal_eval(color_indices)
        except (ValueError, SyntaxError):
            color_indices = []
    if not isinstance(color_indices, (list, tuple)):
        color_indices = []
    out: List[Optional[int]] = []
    for v in list(color_indices)[:length]:
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            out.append(None)
    out += [None] * max(0, length - len(out))
    return out


# ---------- LOAD SAVE ----------
save_path: Path = args.savegame
if not save_path.exists():
    raise FileNotFoundError(f"Save file not found: {save_path}")

save = AsaSave(save_path)

map_folder = save_path.parent.name
map_name = save_path.stem
ark_map = MAP_NAME_MAPPING.get(map_name)
if ark_map is None:
    raise ValueError(f"Unknown map name '{map_name}'. Known: {', '.join(MAP_NAME_MAPPING)}")

# NEW: Output path uses --serverkey
export_folder = Path(args.output) / args.serverkey
export_folder.mkdir(parents=True, exist_ok=True)
json_output_path = export_folder / "TamedDinos.json"

# ---------- PROCESS ----------
dino_api = DinoApi(save)
tamed_dinos: List[Dict[str, Any]] = []

for dino_id, dino in dino_api.get_all_tamed().items():
    if not isinstance(dino, (TamedDino, TamedBaby)):
        continue

    dino_json = dino.to_json_obj()

    # Location & coords (cryopodded tames have no reliable world position)
    loc = safe_location(dino)
    if loc is not None and not getattr(dino, "is_cryopodded", False):
        ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
        coords = loc.as_map_coords(ark_map)
        lat = getattr(coords, "lat", 0.0) if coords else 0.0
        lon = getattr(coords, "long", 0.0) if coords else 0.0
    else:
        ccc, lat, lon = "", 0.0, 0.0

    # Tribe / Tamer
    tribe_id = safe_owner_field(dino, "tamer_tribe_id")
    tamer_name = safe_owner_field(dino, "tamer_string")

    # Fallback: baby claimed or cryo edge-cases
    if (tribe_id == 2000000000 and dino_json.get("TargetingTeam")) or tribe_id is None:
        tribe_id = dino_json.get("TargetingTeam")

    # Base/Added/Mutated stats
    stats_entry: Dict[str, int] = {}
    for prefix, field in STAT_NAME_MAP.items():
        base = getattr(getattr(getattr(dino, "stats", None), "base_stat_points", None), field, 0)
        add = getattr(getattr(getattr(dino, "stats", None), "added_stat_points", None), field, 0)
        mut = getattr(getattr(getattr(dino, "stats", None), "mutated_stat_points", None), field, 0)
        stats_entry[f"{prefix}-w"] = int(base or 0)
        stats_entry[f"{prefix}-t"] = int(add or 0)
        stats_entry[f"{prefix}-m"] = int(mut or 0)

    # Colors
    c0, c1, c2, c3, c4, c5 = pad_colors(dino_json.get("ColorSetIndices", "[]"))

    entry: Dict[str, Any] = {
        "id": str(dino_id),
        "tribeid": tribe_id,
        "tribe": dino_json.get("TribeName", "") or "",
        "tamer": tamer_name or "",
        "imprinter": safe_owner_field(dino, "imprinter") or "",
        "imprint": float(getattr(dino, "percentage_imprinted", 0.0) or 0.0),
        "creature": f"{dino.get_short_name()}_C",
        "name": getattr(dino, "tamed_name", "") or "",
        "sex": "Female" if getattr(dino, "is_female", False) else "Male",
        "base": getattr(getattr(dino, "stats", None), "base_level", None),
        "lvl": getattr(getattr(dino, "stats", None), "current_level", None),
        "lat": lat,
        "lon": lon,
        "cryo": bool(getattr(dino, "is_cryopodded", False)),
        "ccc": ccc,
        "dinoid": str(dino_id),
        "isMating": False,
        "isNeutered": False,
        "isClone": False,
        "maturation": float(getattr(dino, "percentage_matured", 100.0)) if isinstance(dino, TamedBaby) else "100",
        "traits": [],
        "inventory": [],
        "is_wild_tamed": bool(is_wild_tamed(dino)),
        "tamedAtTime": convert_tamed_time(dino_json.get("TamedTimeStamp")),
        "mut-f": dino_json.get("RandomMutationsFemale"),
        "mut-m": dino_json.get("RandomMutationsMale"),
        "c0": c0, "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
    }

    # Merge stats
    entry.update(stats_entry)

    # Merge parsed added stat values (hp-a, stam-a, ...)
    stat_values = dino_json.get("StatValues", "")
    if stat_values:
        entry.update(extract_added_stat_values(stat_values))

    tamed_dinos.append(entry)

# ---------- WRITE JSON (atomic) ----------
payload = {"map": map_folder, "data": tamed_dinos}

with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(export_folder), suffix=".tmp") as tf:
    json.dump(payload, tf, ensure_ascii=False, separators=(",", ":"))
    tmp_name = tf.name

os.replace(tmp_name, json_output_path)

print(f"Saved {len(tamed_dinos)} tamed dinos to {json_output_path}")
print(f"Script runtime: {time() - start_time:.2f} seconds")
