#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Expected Output from ASV
#     {
#       "tribeid": 713052979,
#       "tribe": "Tribe of Survivor",
#       "struct": "StructureBP_Roof_Corner_Right_Inverted_Wood_C",
#       "name": "",
#       "lat": 60.857887,
#       "lon": 58.53211,
#       "ccc": "68256,87 86863,1 -20322,7",
#       "created": "19.03.2025 12:09:57",
#       "inventory": []
#     },

import argparse
import json
import os
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional, Tuple
from tempfile import NamedTemporaryFile

from arkparse.api import StructureApi
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from datetime import datetime

start_time = time()

# ---------- CLI ----------
parser = argparse.ArgumentParser(description="Export ASA structures to JSON.")
parser.add_argument("--savegame", type=Path, required=True, help="Path to .ark savegame file")
parser.add_argument("--output", type=Path, required=True, help="Output directory")
args = parser.parse_args()

# ---------- CONSTANTS ----------
MAP_NAME_MAPPING = {
    "Aberration_WP": ArkMap.ABERRATION,
    "Extinction_WP": ArkMap.EXTINCTION,
    "TheIsland_WP": ArkMap.THE_ISLAND,
    "Ragnarok_WP": ArkMap.RAGNAROK,
    "ScorchedEarth_WP": ArkMap.SCORCHED_EARTH,
    "TheCenter_WP": ArkMap.THE_CENTER,
    "Astraeos_WP": ArkMap.ASTRAEOS,
}

# ---------- HELPERS ----------
def get_map_key_from_savepath(save_path: Path) -> Tuple[str, str]:
    """Extract map folder and map key from savegame path."""
    return save_path.parent.name, save_path.stem


def resolve_coords(structure: Any, ark_map: Optional[ArkMap]) -> Tuple[Tuple[float, float], str]:
    """Return (lat, lon) and ccc string for a structure."""
    if not getattr(structure, "location", None):
        return (0.0, 0.0), ""
    loc = structure.location
    ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
    if ark_map is None:
        return (0.0, 0.0), ccc
    try:
        coords = loc.as_map_coords(ark_map)
        if coords is not None:
            return (coords.lat, coords.long), ccc
    except Exception:
        return (0.0, 0.0), ccc
    return (0.0, 0.0), ccc


def parse_created(ts: Optional[str]) -> Optional[str]:
    """Parse ASA timestamp 'YYYY.MM.DD-HH.MM.SS' to 'DD.MM.YYYY HH:MM:SS'."""
    if not ts:
        return None
    try:
        dt = datetime.strptime(ts, "%Y.%m.%d-%H.%M.%S")
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except ValueError:
        return None


# ---------- LOAD SAVE ----------
save_path: Path = args.savegame
if not save_path.exists():
    raise FileNotFoundError(f"Save file not found at: {save_path}")

map_folder, map_name_key = get_map_key_from_savepath(save_path)
ark_map = MAP_NAME_MAPPING.get(map_name_key)

export_folder = args.output / map_folder
export_folder.mkdir(parents=True, exist_ok=True)
json_output_path = export_folder / f"{map_folder}_Structures.json"

save = AsaSave(save_path)
structure_api = StructureApi(save)

# ---------- PROCESS ----------
out_data: List[Dict[str, Any]] = []

for structure in structure_api.get_all_fast():
    owner_name = structure.object.get_property_value("OwnerName")
    if owner_name is None:
        continue

    tribe_id = structure.object.get_property_value("TargetingTeam")
    if tribe_id is None:
        continue

    created = parse_created(structure.object.get_property_value("OriginalPlacedTimeStamp", 0))
    (lat, lon), ccc = resolve_coords(structure, ark_map)

    entry = {
        "tribeid": tribe_id,
        "tribe": owner_name,
        "struct": f"{structure.get_short_name()}_C",
        "name": structure.object.get_property_value("BoxName"),
        "lat": lat,
        "lon": lon,
        "ccc": ccc,
        "created": created,
        "inventory": [],
    }
    out_data.append(entry)

# ---------- WRITE JSON (atomic) ----------
payload = {"map": map_folder, "data": out_data}

with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(export_folder), suffix=".tmp") as tf:
    json.dump(payload, tf, ensure_ascii=False, separators=(",", ":"))
    tmp_name = tf.name

os.replace(tmp_name, json_output_path)

print(f"Saved {len(out_data)} data to {json_output_path}")
print(f"Script runtime: {time() - start_time:.2f} seconds")