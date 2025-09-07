#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Export ASA players to JSON (very simple)
# Output path:
#   <output>/<serverkey>/Players.json
#
# Example:
#   python export_players.py --serverkey="extinction_a" \
#       --savegame="../temp/extinction_a/.../Extinction_WP.ark" \
#       --output=../output
#   => ../output/extinction_a/Players.json

import os
import json
import argparse
from pathlib import Path
from time import time
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from arkparse.saves.asa_save import AsaSave
from arkparse.api.player_api import PlayerApi

start_time = time()

EPOCH_LOGIN = datetime(2019, 1, 1, tzinfo=timezone.utc)

# ---------- CLI ----------
parser = argparse.ArgumentParser(description="Export ASA players to JSON (simple).")
parser.add_argument("--savegame", type=Path, required=True, help="Path to .ark savegame file")
parser.add_argument("--output", type=Path, required=True, help="Base output directory. Final JSON will be <output>/<serverkey>/Players.json")
parser.add_argument("--serverkey", type=str, required=True, help="Server key used to build output folder name (e.g. extinction_a)")
args = parser.parse_args()

# ---------- HELPER ----------
def get_map_key_from_savepath(save_path: Path) -> Tuple[str, str]:
    """Extract map folder and map key from savegame path."""
    return save_path.parent.name, save_path.stem

def convert_login_time_to_mysql(ts) -> str | None:
    if ts is None:
        return None
    try:
        dt = EPOCH_LOGIN + timedelta(seconds=float(ts))
        return dt.strftime("%Y-%m-%d %H:%M:%S")  # MySQL DATETIME
    except Exception:
        return None

def is_active_within_months(login_time, months: int = 2) -> bool:
    """
    True, wenn LoginTime innerhalb der letzten 'months' Monate liegt.
    Näherung: months * 30 Tage (60 Tage bei 2 Monaten).
    """
    if login_time is None:
        return False
    try:
        last_dt = EPOCH_LOGIN + timedelta(seconds=float(login_time))
        now = datetime.now(timezone.utc)
        return last_dt >= now - timedelta(days=months * 30)
    except Exception:
        return False

# ---------- LOAD SAVE ----------
save_path: Path = args.savegame
map_folder, map_name_key = get_map_key_from_savepath(save_path)
if not save_path.exists():
    raise FileNotFoundError(f"Save file not found: {save_path}")

save = AsaSave(save_path)

# ---------- PLAYER API ----------
player_api = PlayerApi(save)

tribes_by_id: Dict[int, str] = {}
for tribe in getattr(player_api, "tribes", []):
    try:
        tid = getattr(tribe, "tribe_id", None)
        name = getattr(tribe, "name", None)
        if name in (None, "") and hasattr(tribe, "tribe_name"):
            name = getattr(tribe, "tribe_name", "")

        # Fallback über to_json_obj(), falls vorhanden
        if (tid is None or name in (None, "")) and hasattr(tribe, "to_json_obj"):
            tj = tribe.to_json_obj() or {}
            tid = tid if tid is not None else tj.get("TribeID", None)
            name = name if name not in (None, "") else tj.get("TribeName", "")

        if tid is None:
            continue  # ohne ID kein Mapping
        tribes_by_id[int(tid)] = str(name or "")
    except Exception:
        continue

players: List[Dict[str, Any]] = []
for player in getattr(player_api, "players", []):
    last_login = convert_login_time_to_mysql(player.login_time)

    if player.tribe is None:
        continue

    entry: Dict[str, Any] = {
        "playerid": str(player.id_),
        "steam": player.name,
        "name": player.char_name,
        "tribeid": player.tribe,
        "tribe": tribes_by_id.get(player.tribe),
        "sex": "Female" if player.config.is_female else "Male",
        "lvl": player.stats.level,
        "lat": 0.0,
        "lon": 0.0,
        "hp": player.stats.stats.health,
        "stam": player.stats.stats.stamina,
        "melee": player.stats.stats.melee_damage,
        "weight": player.stats.stats.weight,
        "speed": player.stats.stats.movement_speed,
        "food": player.stats.stats.food,
        "water": player.stats.stats.water,
        "oxy": player.stats.stats.oxygen,
        "craft": player.stats.stats.crafting_speed,
        "fort": player.stats.stats.fortitude,
        "active": is_active_within_months(player.login_time, months=2),
        "last_login": last_login,
        "ccc": "0 0 0",
        "steamid": str(player.unique_id),
        "netAddress": player.ip_address,
        "achievements": [],
        "inventory": [],
        "deaths": int(player.nr_of_deaths),
        "last_death": player.last_time_died,
    }

    players.append(entry)

# ---------- WRITE JSON (atomic) ----------
export_folder = Path(args.output) / args.serverkey
export_folder.mkdir(parents=True, exist_ok=True)
json_output_path = export_folder / "Players.json"

payload = {"map": map_folder, "data": players}

with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(export_folder), suffix=".tmp") as tf:
    json.dump(payload, tf, ensure_ascii=False, separators=(",", ":"))
    tmp_name = tf.name

os.replace(tmp_name, json_output_path)

print(f"Saved {len(players)} players to {json_output_path}")
print(f"Script runtime: {time() - start_time:.2f} seconds")