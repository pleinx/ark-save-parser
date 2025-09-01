#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ASV-style export of **wild tamable** dinos
# Output path requirement:
#   <output>/<serverkey>/WildDinos.json
# Example:
#   python export_wild.py --serverkey="extinction_a" \
#       --savegame="../temp/extinction_a/.../Extinction_WP.ark" \
#       --output=../output
#   => ../output/extinction_a/WildDinos.json

import argparse
import json
import os
from uuid import UUID
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional, Tuple
from tempfile import NamedTemporaryFile

from arkparse.api.dino_api import DinoApi, Dino
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave

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

# ---------- ARGS ----------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export ASA wild tamable dinos to JSON.")
    p.add_argument("--savegame", type=Path, required=True, help="Path to .ark savegame file")
    p.add_argument("--output", type=Path, required=True, help="Base output directory (root). Final JSON will be <output>/<serverkey>/WildDinos.json")
    p.add_argument("--serverkey", type=str, required=True, help="Server key used to build output folder name (e.g. extinction_a)")
    p.add_argument("--max-level", type=int, default=150, help="Max level for non-bionic dinos")
    p.add_argument("--max-level-bionic", type=int, default=180, help="Max level for bionic dinos")
    return p.parse_args()

# ---------- HELPERS ----------

def is_bionic(class_name: str) -> bool:
    return ("Bionic" in class_name) or ("Tek" in class_name) or ("TEK" in class_name)

def safe_color_indices(raw: Any) -> List[Optional[int]]:
    if raw is None:
        return [None] * 6
    if isinstance(raw, list):
        vals = raw[:6]
        return [int(v) if isinstance(v, (int, float)) else None for v in vals] + [None] * (6 - len(vals))
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                inner = s[1:-1].strip()
                if not inner:
                    return [None] * 6
                parts = [p.strip() for p in inner.split(",")]
                vals: List[Optional[int]] = []
                for p in parts[:6]:
                    try:
                        vals.append(int(float(p)))
                    except ValueError:
                        vals.append(None)
                return vals + [None] * (6 - len(vals))
            except Exception:
                return [None] * 6
    return [None] * 6

def get_server_and_map_key(save_path: Path) -> Tuple[str, str]:
    map_key = save_path.stem
    server_folder = None
    for p in save_path.parents:
        name = p.name
        if name.endswith("_a"):
            server_folder = name
            break
    if server_folder is None:
        # Fallback: best effort
        try:
            server_folder = save_path.parents[5].name
        except Exception:
            server_folder = save_path.parent.name
    return server_folder, map_key

def get_base_stat(stats: Any, stat_field: str) -> int:
    try:
        return int(getattr(stats.base_stat_points, stat_field, 0) or 0)
    except Exception:
        return 0

def within_level_cap(class_name: str, level: Optional[int], cap_normal: int, cap_bionic: int) -> bool:
    if level is None:
        return False
    return level <= (cap_bionic if is_bionic(class_name) else cap_normal)

def _safe_int_id(value: Any) -> Optional[int]:
    try:
        i = int(str(value))
        if -(2**63) <= i < 2**63:
            return i
        return None
    except Exception:
        return None

def build_entry(
    dino_id: Any,
    dino: Dino,
    dino_json: Dict[str, Any],
    coords: Tuple[float, float],
    ccc: str,
) -> Dict[str, Any]:
    lat, lon = coords
    dino_class = f"{dino.get_short_name()}_C"
    s = dino.stats
    colors = safe_color_indices(dino_json.get("ColorSetIndices"))
    int_id = _safe_int_id(dino_id)

    return {
        "id": int_id if int_id is not None else str(dino_id),
        "creature": dino_class,
        "sex": "Female" if dino.is_female else "Male",
        "lvl": (s.base_level if s else None),
        "lat": lat,
        "lon": lon,
        "hp": get_base_stat(s, STAT_NAME_MAP["hp"]),
        "stam": get_base_stat(s, STAT_NAME_MAP["stam"]),
        "melee": get_base_stat(s, STAT_NAME_MAP["melee"]),
        "weight": get_base_stat(s, STAT_NAME_MAP["weight"]),
        "speed": get_base_stat(s, STAT_NAME_MAP["speed"]),
        "food": get_base_stat(s, STAT_NAME_MAP["food"]),
        "oxy": get_base_stat(s, STAT_NAME_MAP["oxy"]),
        "craft": get_base_stat(s, STAT_NAME_MAP["craft"]),
        "c0": colors[0],
        "c1": colors[1],
        "c2": colors[2],
        "c3": colors[3],
        "c4": colors[4],
        "c5": colors[5],
        "ccc": ccc,
        "dinoid": str(dino_id),
        "tameable": True,
        "trait": str(dino_json.get("GeneTraits", "") or ""),
    }

def resolve_coords(dino: Dino, ark_map: Optional[ArkMap]) -> Tuple[Tuple[float, float], str]:
    if dino.is_cryopodded or not dino.location:
        return (0.0, 0.0), ""
    ccc = f"{dino.location.x:.2f} {dino.location.y:.2f} {dino.location.z:.2f}"
    if ark_map is None:
        return (0.0, 0.0), ccc
    try:
        coords = dino.location.as_map_coords(ark_map)
        if coords is not None:
            return (coords.lat, coords.long), ccc
    except Exception:
        pass
    return (0.0, 0.0), ccc

def _json_default(o: Any):
    if isinstance(o, (UUID, Path)):
        return str(o)
    return str(o)

# ---------- PROCESS ----------

start_time = time()
args = parse_args()

if not args.savegame.exists():
    raise FileNotFoundError(f"Save file not found at: {args.savegame}")

server_folder, map_key = get_server_and_map_key(args.savegame)
ark_map = MAP_NAME_MAPPING.get(map_key)

# NEW: respect --serverkey, final path is <output>/<serverkey>/WildDinos.json
export_folder = Path(args.output) / args.serverkey
export_folder.mkdir(parents=True, exist_ok=True)
json_output_path = export_folder / "WildDinos.json"

save = AsaSave(args.savegame)
dino_api = DinoApi(save)

out_data: List[Dict[str, Any]] = []

for dino_id, dino in dino_api.get_all_wild_tamables().items():
    if not isinstance(dino, Dino):
        continue

    dino_class = f"{dino.get_short_name()}_C"
    lvl = (dino.stats.base_level if dino.stats else None)

    if "_Corrupt" in dino_class:
        continue
    if not within_level_cap(dino_class, lvl, args.max_level, args.max_level_bionic):
        continue

    dino_json = dino.to_json_obj()
    (lat, lon), ccc = resolve_coords(dino, ark_map)
    entry = build_entry(dino_id, dino, dino_json, (lat, lon), ccc)
    out_data.append(entry)

# ---------- WRITE JSON (atomic) ----------
payload = {"map": server_folder, "data": out_data}

with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(export_folder), suffix=".tmp") as tf:
    json.dump(payload, tf, ensure_ascii=False, separators=(",", ":"), default=_json_default)
    tmp_name = tf.name

os.replace(tmp_name, json_output_path)

print(f"Saved {len(out_data)} wild tamables to {json_output_path}")
print(f"Script runtime: {time() - start_time:.2f} seconds")
