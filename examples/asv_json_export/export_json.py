#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified ASA JSON Exporter
- Option 2: Eigene Prozesse ohne Pool → jeder Export-Prozess beendet sich direkt nach Fertigstellung (RAM wird freigegeben).
- Priorität: 'tamed' zuerst, dann 'structures', danach die übrigen Typen in der ursprünglichen Reihenfolge.
- Parallelmodus (--parallel=1) startet alle angeforderten Typen gleichzeitig als Einmal-Prozesse.
- Serieller Modus (--parallel=0, Default) lädt das Save genau einmal und führt Exporte nacheinander aus.
- Ausgabeformat: [OK][type] Wrote  XXXX entries in YY.yy secs -> <pfad>
- Neues Flag: --withcryo=1 aktiviert Cryopod-Dinos **nur** für den Tamed-Export. Für andere Typen wird es ignoriert.

Beispiele:
  py asv_json_export/export_json.py --type="all" --serverkey="staging_a" --savegame=".../Astraeos_WP.ark" --output=../output
  py asv_json_export/export_json.py --type="tamed" --withcryo=1 --serverkey="staging_a" --savegame=".../Astraeos_WP.ark" --output=../output
  py asv_json_export/export_json.py --type="players,tamed" --parallel=1 --withcryo=0 --serverkey="staging_a" --savegame=".../Astraeos_WP.ark" --output=../output
"""

from __future__ import annotations

import argparse
import ast
import configparser
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from zoneinfo import ZoneInfo
import multiprocessing as mp
from pprint import pprint
from datetime import datetime, timedelta

try:
    import orjson
except ImportError:
    orjson = None

# arkparse
from arkparse.saves.asa_save import AsaSave
from arkparse.enums import ArkMap
from arkparse.api.player_api import PlayerApi
from arkparse.api.dino_api import DinoApi, Dino, TamedDino, TamedBaby
from arkparse.api import StructureApi
from arkparse.helpers.dino.is_wild_tamed import is_wild_tamed
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model.structures import StructureWithInventory
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.parsing.struct.actor_transform import MapCoordinateParameters

def get_mp_context():
    """
    Windows: spawn (Pflicht)
    Linux/Unix: fork (schneller), fallback spawn falls fork nicht verfügbar ist.
    """
    if sys.platform.startswith("win"):
        return mp.get_context("spawn")
    try:
        return mp.get_context("fork")
    except ValueError:
        return mp.get_context("spawn")


# ---------- CLI ----------

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Unified ASA JSON Exporter")
    p.add_argument("--savegame", type=Path, required=True, help="Pfad zur .ark Datei")
    p.add_argument("--output", type=Path, required=True, help="Basis-Output-Ordner")
    p.add_argument("--serverkey", type=str, required=True, help="Server-Key (z.B. extinction_a)")
    p.add_argument(
        "--type",
        type=str,
        required=True,
        help='Exporttypen, kommasepariert. Erlaubt: "players,structures,tamed,wild" oder "all"',
    )
    # Parallel-Flag
    p.add_argument("--parallel", type=int, default=1, choices=(0, 1), help="0=seriell, 1=parallel (Einmal-Prozesse, default)")
    # Wild-spezifische Parameter
    p.add_argument("--max-level", type=int, default=150, help="Levelcap für normale Wild-Dinos")
    p.add_argument("--max-level-bionic", type=int, default=180, help="Levelcap für Bionic/TEK Wild-Dinos")
    # Tamed-spezifisch
    p.add_argument("--withcryo", type=int, default=1, choices=(0, 1),
                   help="1 = Cryopod-Dinos einbeziehen beim Tamed-Export, 1 = mit Cryos (Default). Für andere Typen ignoriert.")
    p.add_argument("--output-mode", type=str, default="json",
                   help='Ausgabeziel: "json", "db" oder "json,db" (DB aktuell für players, tamed und structures; wild schreibt weiter JSON)')
    p.add_argument("--db-config", type=Path, default=None,
                   help="Pfad zu db.ini für --output-mode=db")
    p.add_argument("--debug", type=str, default="",
                   help='Debug-Ausgaben, kommasepariert. Aktuell: "performance"')
    return p

# ---------- Configuration ----------

SUPPORTED_TYPES = {"players", "structures", "tamed", "wild"}
SUPPORTED_OUTPUT_MODES = {"json", "db"}
SUPPORTED_DEBUG_MODES = {"performance"}
DB_SUPPORTED_TYPES = {"players", "tamed", "structures"}
# TODO: Add a proper MariaDB export for wild dinos. Until then, wild must
# still write WildDinos.json even when --output-mode=db was requested.
DB_JSON_FALLBACK_TYPES = {"wild"}
DB_PLAYERS_TABLE_DEFAULT = "pix_ark_sa_players"
DB_TAMED_TABLE_DEFAULT = "pix_ark_sa_tamed_arkparse"
DB_STRUCTURES_TABLE_DEFAULT = "pix_ark_sa_structures"
DB_STRUCTURE_INVENTORIES_TABLE_DEFAULT = "pix_ark_sa_structure_inventories"
STRUCTURE_INVENTORY_EXPORT_CLASSES = {"Market_C", "Bookshelf_C"}
DINO_CLASS_SEX_OVERRIDES = {
    "Lumina_Character_BP_C": "Female",
    "Umbra_Character_BP_C": "Male",
}

MAP_NAME_MAPPING: Dict[str, ArkMap] = {
    "Aberration_WP": ArkMap.ABERRATION,
    "Extinction_WP": ArkMap.EXTINCTION,
    "Genesis_WP": ArkMap.GENESIS1,
    "TheIsland_WP": ArkMap.THE_ISLAND,
    "Ragnarok_WP": ArkMap.RAGNAROK,
    "ScorchedEarth_WP": ArkMap.SCORCHED_EARTH,
    "TheCenter_WP": ArkMap.THE_CENTER,
    "Astraeos_WP": ArkMap.ASTRAEOS,
    "Valguero_WP": ArkMap.VALGUERO,
    "LostColony_WP": ArkMap.LOST_COLONY,
}

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

ADDED_KEY_MAP = {
    "health": "hp-a",
    "stamina": "stam-a",
    "melee_damage": "melee-a",
    "weight": "weight-a",
    "movement_speed": "speed-a",
    "food": "food-a",
    "oxygen": "oxy-a",
}

EPOCH_LOGIN = datetime(2019, 1, 1, tzinfo=timezone.utc)  # für Player LoginTime Konvertierung

# ---------- Utilities ----------

def _orjson_options(append_newline: bool = False) -> int:
    if orjson is None:
        return 0

    options = orjson.OPT_NON_STR_KEYS | orjson.OPT_PASSTHROUGH_DATETIME
    if append_newline:
        options |= orjson.OPT_APPEND_NEWLINE
    return options

def json_dumps_bytes(obj: Any, append_newline: bool = False, ensure_ascii: bool = False) -> bytes:
    if orjson is not None:
        return orjson.dumps(obj, default=json_default, option=_orjson_options(append_newline))

    text = json.dumps(
        obj,
        ensure_ascii=ensure_ascii,
        default=json_default,
        separators=(",", ":"),
    )
    if append_newline:
        text += "\n"
    return text.encode("utf-8")

def ensure_export_folder(base_output: Path, serverkey: str) -> Path:
    out = base_output / serverkey
    out.mkdir(parents=True, exist_ok=True)
    return out

def parse_output_modes(mode_arg: str) -> set[str]:
    parts = [p.strip().lower() for p in (mode_arg or "json").split(",") if p.strip()]
    if not parts:
        raise ValueError("--output-mode darf nicht leer sein")

    modes = set(parts)
    unknown = modes - SUPPORTED_OUTPUT_MODES
    if unknown:
        raise ValueError(f"Unbekannte --output-mode Werte: {', '.join(sorted(unknown))}. Erlaubt: json, db")
    return modes

def validate_output_modes(types: List[str], output_modes: set[str]) -> None:
    if "db" not in output_modes:
        return

    if "json" not in output_modes:
        unsupported = [t for t in types if t not in DB_SUPPORTED_TYPES and t not in DB_JSON_FALLBACK_TYPES]
        if unsupported:
            raise ValueError(
                "--output-mode=db unterstützt aktuell nur type=players,tamed,structures. "
                "type=wild fällt bis zum DB-Export automatisch auf JSON zurück. "
                f"Nicht unterstützt: {', '.join(unsupported)}"
            )

def parse_debug_modes(debug_arg: str) -> set[str]:
    parts = [p.strip().lower() for p in (debug_arg or "").split(",") if p.strip()]
    if not parts:
        return set()

    modes = set(parts)
    unknown = modes - SUPPORTED_DEBUG_MODES
    if unknown:
        raise ValueError(f"Unbekannte --debug Werte: {', '.join(sorted(unknown))}. Erlaubt: performance")
    return modes

def perf_enabled(debug_modes: Optional[set[str]]) -> bool:
    return bool(debug_modes and "performance" in debug_modes)

def perf_log(debug_modes: Optional[set[str]], scope: str, label: str, started_at: float, count: Optional[int] = None) -> None:
    if not perf_enabled(debug_modes):
        return

    count_part = f" ({count} items)" if count is not None else ""
    print(f"[PERF][{scope}] {label}: {time() - started_at:.3f}s{count_part}", flush=True)

def perf_add(timings: Optional[Dict[str, float]], label: str, started_at: float) -> None:
    if timings is None:
        return
    timings[label] = timings.get(label, 0.0) + (time() - started_at)

def perf_log_breakdown(debug_modes: Optional[set[str]], scope: str, label: str, timings: Optional[Dict[str, float]]) -> None:
    if not perf_enabled(debug_modes) or not timings:
        return

    for item_label, elapsed in sorted(timings.items(), key=lambda item: item[1], reverse=True):
        print(f"[PERF][{scope}] {label}.{item_label}: {elapsed:.3f}s", flush=True)

def _config_or_env(config: configparser.ConfigParser, key: str, env_name: str, default: Optional[str] = None) -> Optional[str]:
    env_value = os.environ.get(env_name)
    if env_value not in (None, ""):
        return env_value
    if config.has_option("database", key):
        return config.get("database", key)
    return default

def _validate_table_name(table: Optional[str], label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", table or ""):
        raise ValueError(f"Ungültiger Tabellenname in DB config ({label}): {table!r}")
    return str(table)

def load_db_options(config_path: Optional[Path]) -> Dict[str, Any]:
    config = configparser.ConfigParser()
    if config_path is not None:
        if not config_path.exists():
            raise FileNotFoundError(f"DB config nicht gefunden: {config_path}")
        config.read(config_path, encoding="utf-8")

    database = _config_or_env(config, "database", "ARK_DB_NAME")
    user = _config_or_env(config, "user", "ARK_DB_USER")
    password = _config_or_env(config, "password", "ARK_DB_PASSWORD", "")

    missing = [name for name, value in (("database", database), ("user", user)) if not value]
    if missing:
        source = str(config_path) if config_path else "Environment"
        raise ValueError(f"DB config unvollständig ({source}), fehlt: {', '.join(missing)}")

    tamed_table = _validate_table_name(
        _config_or_env(config, "tamed_table", "ARK_DB_TAMED_TABLE", DB_TAMED_TABLE_DEFAULT),
        "tamed_table",
    )
    players_table = _validate_table_name(
        _config_or_env(config, "players_table", "ARK_DB_PLAYERS_TABLE", DB_PLAYERS_TABLE_DEFAULT),
        "players_table",
    )
    structures_table = _validate_table_name(
        _config_or_env(config, "structures_table", "ARK_DB_STRUCTURES_TABLE", DB_STRUCTURES_TABLE_DEFAULT),
        "structures_table",
    )
    structure_inventories_table = _validate_table_name(
        _config_or_env(config, "structure_inventories_table", "ARK_DB_STRUCTURE_INVENTORIES_TABLE", DB_STRUCTURE_INVENTORIES_TABLE_DEFAULT),
        "structure_inventories_table",
    )

    batch_size_raw = _config_or_env(config, "batch_size", "ARK_DB_BATCH_SIZE", "1000")
    try:
        batch_size = max(1, int(batch_size_raw or 1000))
    except ValueError:
        raise ValueError(f"Ungültige DB batch_size: {batch_size_raw!r}") from None

    return {
        "host": _config_or_env(config, "host", "ARK_DB_HOST", "127.0.0.1"),
        "port": int(_config_or_env(config, "port", "ARK_DB_PORT", "3306") or 3306),
        "database": database,
        "user": user,
        "password": password,
        "charset": _config_or_env(config, "charset", "ARK_DB_CHARSET", "utf8mb4"),
        "unix_socket": _config_or_env(config, "unix_socket", "ARK_DB_UNIX_SOCKET"),
        "connect_timeout": int(_config_or_env(config, "connect_timeout", "ARK_DB_CONNECT_TIMEOUT", "10") or 10),
        "players_table": players_table,
        "tamed_table": tamed_table,
        "structures_table": structures_table,
        "structure_inventories_table": structure_inventories_table,
        "batch_size": batch_size,
    }

def atomic_write_json(obj: Any, target: Path, export_folder: Path) -> None:
    """
    CIFS-robustes atomic write (orjson-only):
    - Temp file IM Zielordner (target.parent) anlegen (wichtig bei SMB/CIFS)
    - orjson für schnelle Serialisierung
    - Fallback-Strategie, falls os.replace() auf CIFS zickt
    """
    target = Path(target)
    target_parent = target.parent
    target_parent.mkdir(parents=True, exist_ok=True)

    tmp_name: Optional[str] = None
    try:
        with NamedTemporaryFile("wb", delete=False, dir=str(target_parent), suffix=".tmp") as tf:
            tf.write(json_dumps_bytes(obj, append_newline=True))
            tmp_name = tf.name

        # Primary attempt
        try:
            os.replace(tmp_name, str(target))
        except Exception:
            # CIFS fallback: remove target first then replace
            try:
                if target.exists():
                    target.unlink()
            except Exception:
                pass
            os.replace(tmp_name, str(target))

    finally:
        # Wenn replace erfolgreich war, existiert tmp nicht mehr.
        # Wenn vorher was schief ging, räumen wir auf.
        if tmp_name and os.path.exists(tmp_name):
            try:
                os.unlink(tmp_name)
            except Exception:
                pass

def _connect_mariadb(db_options: Dict[str, Any]):
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError(
            "Für --output-mode=db wird PyMySQL benötigt. Installation z.B.: pip install pymysql"
        ) from exc

    connect_args = {
        "host": db_options["host"],
        "port": db_options["port"],
        "user": db_options["user"],
        "password": db_options["password"],
        "database": db_options["database"],
        "charset": db_options["charset"],
        "autocommit": False,
        "connect_timeout": db_options["connect_timeout"],
    }
    if db_options.get("unix_socket"):
        connect_args["unix_socket"] = db_options["unix_socket"]

    return pymysql.connect(**connect_args)

def _chunked_rows(rows: List[Tuple[Any, ...]], size: int):
    for start in range(0, len(rows), size):
        yield rows[start:start + size]

def _safe_scalar(value: Any, default: str = "") -> str:
    if value is None or isinstance(value, (dict, list, tuple)):
        return default
    return str(value).strip()

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def _json_for_db(value: Any, ensure_ascii: bool = False) -> str:
    return json_dumps_bytes(value, ensure_ascii=ensure_ascii).decode("utf-8")

def build_players_db_rows(payload: Dict[str, Any], serverkey: str) -> List[Tuple[Any, ...]]:
    rows: List[Tuple[Any, ...]] = []

    for data in payload.get("data") or []:
        if not isinstance(data, dict):
            continue

        steamid = _safe_scalar(data.get("steamid"))
        if not steamid:
            continue

        rows.append(
            (
                steamid,
                _safe_int(data.get("playerid")),
                _safe_scalar(data.get("name")),
                _json_for_db(data.get("achievements"), ensure_ascii=True),
                _json_for_db(data.get("inventory"), ensure_ascii=True),
                _safe_int(data.get("lvl")),
                serverkey,
                _safe_float(data.get("lat")),
                _safe_float(data.get("lon")),
            )
        )

    return rows

def write_players_mariadb(
    payload: Dict[str, Any],
    serverkey: str,
    db_options: Dict[str, Any],
    debug_modes: Optional[set[str]] = None,
) -> int:
    rows_started = time()
    rows = build_players_db_rows(payload, serverkey)
    perf_log(debug_modes, "db:players", "build rows", rows_started, len(rows))

    if not payload.get("data"):
        return 0
    if not rows:
        raise ValueError(f"Keine gültigen players DB-Zeilen für serverkey={serverkey}; breche DB-Sync sicherheitshalber ab")

    table = f"`{db_options['players_table']}`"
    insert_sql = f"""
        INSERT INTO {table}(
            `player_id`, `player_ign_id`, `player_name`, `archivements_json`, `inventory_json`,
            `level`, `server_key`, `lat`, `lon`, `last_update_date`, `created_date`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `player_ign_id` = VALUES(player_ign_id),
            `server_key` = VALUES(server_key),
            `player_name` = VALUES(player_name),
            `level` = GREATEST(`level`, VALUES(level)),
            `last_update_date` = VALUES(last_update_date)
    """

    connect_started = time()
    conn = _connect_mariadb(db_options)
    perf_log(debug_modes, "db:players", "connect", connect_started)
    try:
        with conn.cursor() as cursor:
            now_started = time()
            cursor.execute("SELECT NOW()")
            sync_started_at = cursor.fetchone()[0]
            perf_log(debug_modes, "db:players", "select sync timestamp", now_started)

            upsert_started = time()
            chunk_count = 0
            for chunk in _chunked_rows(rows, db_options["batch_size"]):
                chunk_count += 1
                cursor.executemany(insert_sql, [row + (sync_started_at, sync_started_at) for row in chunk])
            perf_log(debug_modes, "db:players", f"upsert chunks={chunk_count}", upsert_started, len(rows))

            cleanup_started = time()
            cursor.execute(
                f"DELETE FROM {table} WHERE `server_key` = %s AND (`last_update_date` IS NULL OR `last_update_date` < %s)",
                (serverkey, sync_started_at),
            )
            perf_log(debug_modes, "db:players", "cleanup stale rows", cleanup_started, cursor.rowcount)

        commit_started = time()
        conn.commit()
        perf_log(debug_modes, "db:players", "commit", commit_started)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return len(rows)

def build_tamed_db_rows(payload: Dict[str, Any], serverkey: str) -> List[Tuple[Any, ...]]:
    rows: List[Tuple[Any, ...]] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for data in payload.get("data") or []:
        if not isinstance(data, dict):
            continue

        try:
            tribe_id = int(data.get("tribeid") or 0)
        except (TypeError, ValueError):
            tribe_id = 0

        dino_id_value = data.get("id")
        dino_id = "" if isinstance(dino_id_value, (dict, list, tuple)) or dino_id_value is None else str(dino_id_value).strip()

        if tribe_id <= 0 or tribe_id == 2000000000 or dino_id == "":
            continue

        tame_id = "TID_" + hashlib.md5((dino_id + serverkey).encode("utf-8")).hexdigest()
        sub_map_value = data.get("biom")
        sub_map = "" if isinstance(sub_map_value, (dict, list, tuple)) or sub_map_value is None else str(sub_map_value).strip()
        tamed_time = data.get("tamedAtTime") or now

        try:
            lvl = int(data.get("lvl") or 0)
        except (TypeError, ValueError):
            lvl = 0

        rows.append(
            (
                tame_id,
                dino_id,
                tribe_id,
                serverkey,
                sub_map or None,
                _json_for_db(data, ensure_ascii=True),
                str(data.get("creature") or ""),
                str(data.get("sex") or ""),
                lvl,
                str(tamed_time),
            )
        )

    return rows

def write_tamed_mariadb(
    payload: Dict[str, Any],
    serverkey: str,
    db_options: Dict[str, Any],
    debug_modes: Optional[set[str]] = None,
) -> int:
    rows_started = time()
    rows = build_tamed_db_rows(payload, serverkey)
    perf_log(debug_modes, "db:tamed", "build rows", rows_started, len(rows))
    if not payload.get("data"):
        return 0
    if not rows:
        raise ValueError(f"Keine gültigen tamed DB-Zeilen für serverkey={serverkey}; breche DB-Sync sicherheitshalber ab")

    table = f"`{db_options['tamed_table']}`"
    insert_sql = f"""
        INSERT INTO {table}(
            `tamed_id`, `dino_id`, `tribe_id`, `server_key`, `sub_map`, `json_data`,
            `creature`, `sex`, `lvl`, `last_update_date`, `created_date`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `dino_id` = VALUES(dino_id),
            `tribe_id` = VALUES(tribe_id),
            `server_key` = VALUES(server_key),
            `sub_map` = VALUES(sub_map),
            `json_data` = VALUES(json_data),
            `creature` = VALUES(creature),
            `sex` = VALUES(sex),
            `lvl` = VALUES(lvl),
            `last_update_date` = VALUES(last_update_date),
            `created_date` = VALUES(created_date)
    """

    connect_started = time()
    conn = _connect_mariadb(db_options)
    perf_log(debug_modes, "db:tamed", "connect", connect_started)
    try:
        with conn.cursor() as cursor:
            now_started = time()
            cursor.execute("SELECT NOW()")
            sync_started_at = cursor.fetchone()[0]
            perf_log(debug_modes, "db:tamed", "select sync timestamp", now_started)
            upsert_started = time()
            upserted_rows = 0
            chunk_count = 0
            for chunk in _chunked_rows(rows, db_options["batch_size"]):
                chunk_count += 1
                upserted_rows += len(chunk)
                cursor.executemany(insert_sql, [row[:9] + (sync_started_at, row[9]) for row in chunk])
            perf_log(debug_modes, "db:tamed", f"upsert chunks={chunk_count}", upsert_started, upserted_rows)
            cleanup_started = time()
            cursor.execute(
                f"DELETE FROM {table} WHERE `server_key` = %s AND (`last_update_date` IS NULL OR `last_update_date` < %s)",
                (serverkey, sync_started_at),
            )
            perf_log(debug_modes, "db:tamed", "cleanup stale rows", cleanup_started, cursor.rowcount)
        commit_started = time()
        conn.commit()
        perf_log(debug_modes, "db:tamed", "commit", commit_started)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return len(rows)

def build_structures_db_rows(payload: Dict[str, Any], serverkey: str) -> List[Tuple[Any, ...]]:
    rows: List[Tuple[Any, ...]] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for data in payload.get("data") or []:
        if not isinstance(data, dict):
            continue

        structure_class = _safe_scalar(data.get("struct"))
        if structure_class in {"DeathItemCache_C", "DeathItemCache_PlayerDeath_C"}:
            continue

        structure_uuid = _safe_scalar(data.get("id"))
        structure_name_value = data.get("name")
        structure_name = None if isinstance(structure_name_value, (dict, list, tuple)) else structure_name_value
        structure_name_for_hash = _safe_scalar(structure_name_value)
        ccc = _safe_scalar(data.get("ccc"))
        sub_map = _safe_scalar(data.get("biom"))
        structure_id = "SID_" + hashlib.md5(
            (serverkey + ccc + structure_class + structure_name_for_hash).encode("utf-8")
        ).hexdigest()

        json_data = {
            "id": structure_uuid,
            "struct": structure_class,
            "name": structure_name,
            "lat": round(_safe_float(data.get("lat")), 2),
            "lon": round(_safe_float(data.get("lon")), 2),
            "locked": data.get("locked") if data.get("locked") is not None else True,
            "ccc": ccc,
        }
        if sub_map:
            json_data["biom"] = sub_map
        if data.get("inventory"):
            json_data["inventory"] = data.get("inventory")

        rows.append(
            (
                structure_id,
                structure_uuid or None,
                _safe_int(data.get("tribeid")),
                serverkey,
                sub_map or None,
                _json_for_db(json_data),
                _safe_scalar(data.get("created")) or now,
            )
        )

    return rows

def build_structure_inventory_db_rows(payload: Dict[str, Any], serverkey: str) -> List[Tuple[Any, ...]]:
    rows: List[Tuple[Any, ...]] = []

    for data in payload.get("data") or []:
        if not isinstance(data, dict):
            continue

        structure_uuid = _safe_scalar(data.get("id"))
        if not structure_uuid:
            continue

        structure_class = _safe_scalar(data.get("struct"))
        if not structure_class:
            continue

        tribe_name = _safe_scalar(data.get("tribe"))
        structure_name = _safe_scalar(data.get("name"))
        sub_map = _safe_scalar(data.get("biom"))
        items = data.get("items") if isinstance(data.get("items"), list) else []

        json_data = {
            "id": structure_uuid,
            "tribeid": _safe_int(data.get("tribeid")),
            "tribe": tribe_name,
            "struct": structure_class,
            "name": structure_name or None,
        }
        if sub_map:
            json_data["biom"] = sub_map

        rows.append(
            (
                structure_uuid,
                serverkey,
                _safe_int(data.get("tribeid")),
                tribe_name or None,
                structure_class,
                structure_name or None,
                sub_map or None,
                len(items),
                _json_for_db(items),
                _json_for_db(json_data),
            )
        )

    return rows

def write_structures_mariadb(
    structures_payload: Dict[str, Any],
    inventory_payload: Dict[str, Any],
    serverkey: str,
    db_options: Dict[str, Any],
    debug_modes: Optional[set[str]] = None,
) -> Tuple[int, int]:
    rows_started = time()
    structure_rows = build_structures_db_rows(structures_payload, serverkey)
    perf_log(debug_modes, "db:structures", "build rows", rows_started, len(structure_rows))
    inventory_rows_started = time()
    inventory_rows = build_structure_inventory_db_rows(inventory_payload, serverkey)
    perf_log(debug_modes, "db:structure_inventories", "build rows", inventory_rows_started, len(inventory_rows))

    if not structures_payload.get("data"):
        return 0, 0
    if not structure_rows:
        raise ValueError(f"Keine gültigen structures DB-Zeilen für serverkey={serverkey}; breche DB-Sync sicherheitshalber ab")

    structures_table = f"`{db_options['structures_table']}`"
    inventory_table = f"`{db_options['structure_inventories_table']}`"
    structures_sql = f"""
        INSERT INTO {structures_table}(
            `structure_id`, `structure_uuid`, `tribe_id`, `server_key`, `sub_map`,
            `json_data`, `last_update_date`, `created_date`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `structure_uuid` = VALUES(structure_uuid),
            `server_key` = VALUES(server_key),
            `tribe_id` = VALUES(tribe_id),
            `sub_map` = VALUES(sub_map),
            `json_data` = VALUES(json_data),
            `last_update_date` = VALUES(last_update_date),
            `created_date` = VALUES(created_date)
    """
    inventory_sql = f"""
        INSERT INTO {inventory_table}(
            `structure_uuid`, `server_key`, `tribe_id`, `tribe_name`, `struct`,
            `structure_name`, `sub_map`, `items_count`, `items_json`, `json_data`,
            `last_update_date`
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `server_key` = VALUES(server_key),
            `tribe_id` = VALUES(tribe_id),
            `tribe_name` = VALUES(tribe_name),
            `struct` = VALUES(struct),
            `structure_name` = VALUES(structure_name),
            `sub_map` = VALUES(sub_map),
            `items_count` = VALUES(items_count),
            `items_json` = VALUES(items_json),
            `json_data` = VALUES(json_data),
            `last_update_date` = VALUES(last_update_date)
    """

    connect_started = time()
    conn = _connect_mariadb(db_options)
    perf_log(debug_modes, "db:structures", "connect", connect_started)
    try:
        with conn.cursor() as cursor:
            now_started = time()
            cursor.execute("SELECT NOW()")
            sync_started_at = cursor.fetchone()[0]
            perf_log(debug_modes, "db:structures", "select sync timestamp", now_started)

            upsert_started = time()
            structure_chunk_count = 0
            for chunk in _chunked_rows(structure_rows, db_options["batch_size"]):
                structure_chunk_count += 1
                cursor.executemany(structures_sql, [row[:6] + (sync_started_at, row[6]) for row in chunk])
            perf_log(debug_modes, "db:structures", f"upsert chunks={structure_chunk_count}", upsert_started, len(structure_rows))

            inventory_upsert_started = time()
            inventory_chunk_count = 0
            for chunk in _chunked_rows(inventory_rows, db_options["batch_size"]):
                inventory_chunk_count += 1
                cursor.executemany(inventory_sql, [row + (sync_started_at,) for row in chunk])
            perf_log(debug_modes, "db:structure_inventories", f"upsert chunks={inventory_chunk_count}", inventory_upsert_started, len(inventory_rows))

            cleanup_started = time()
            cursor.execute(
                f"DELETE FROM {structures_table} WHERE `server_key` = %s AND (`last_update_date` IS NULL OR `last_update_date` < %s)",
                (serverkey, sync_started_at),
            )
            perf_log(debug_modes, "db:structures", "cleanup stale rows", cleanup_started, cursor.rowcount)

            inventory_cleanup_started = time()
            cursor.execute(
                f"DELETE FROM {inventory_table} WHERE `server_key` = %s AND (`last_update_date` IS NULL OR `last_update_date` < %s)",
                (serverkey, sync_started_at),
            )
            perf_log(debug_modes, "db:structure_inventories", "cleanup stale rows", inventory_cleanup_started, cursor.rowcount)

        commit_started = time()
        conn.commit()
        perf_log(debug_modes, "db:structures", "commit", commit_started)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return len(structure_rows), len(inventory_rows)

def describe_export_target(export_type: str, filename: str, export_folder: Path, output_modes: set[str], db_options: Optional[Dict[str, Any]]) -> str:
    targets: List[str] = []
    writes_json = "json" in output_modes or ("db" in output_modes and export_type in DB_JSON_FALLBACK_TYPES)
    if writes_json and export_type == "structures":
        targets.append(f"{export_folder / 'Structures.json'} + {export_folder / 'StructuresInventory.json'}")
    elif writes_json:
        targets.append(str(export_folder / filename))
    if "db" in output_modes and export_type == "tamed":
        table = db_options["tamed_table"] if db_options else DB_TAMED_TABLE_DEFAULT
        targets.append(f"MariaDB:{table}")
    if "db" in output_modes and export_type == "players":
        table = db_options["players_table"] if db_options else DB_PLAYERS_TABLE_DEFAULT
        targets.append(f"MariaDB:{table}")
    if "db" in output_modes and export_type == "structures":
        structures_table = db_options["structures_table"] if db_options else DB_STRUCTURES_TABLE_DEFAULT
        inventory_table = db_options["structure_inventories_table"] if db_options else DB_STRUCTURE_INVENTORIES_TABLE_DEFAULT
        targets.append(f"MariaDB:{structures_table}")
        targets.append(f"MariaDB:{inventory_table}")
    return " + ".join(targets) if targets else "(no output)"

def get_map_key_from_savepath(save_path: Path) -> Tuple[str, str]:
    """Gibt (map_folder, map_key) zurück"""
    return save_path.parent.name, save_path.stem

def asa_login_to_mysql_local(ts: float | int | None, tz_name: str = "Europe/Berlin") -> Optional[str]:
    if not ts:
        return None
    try:
        x = float(ts)
        # Cisco ASA REST-API Epoch: 01.01.2018 00:00:00 UTC
        asa_base = datetime(2018, 1, 1, tzinfo=ZoneInfo("UTC"))

        # Berechnung
        dt = asa_base + timedelta(seconds=x)
        dt_local = dt.astimezone(ZoneInfo(tz_name))

        return dt_local.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def is_active_within_months(login_time: float | int | None, months: int = 2) -> bool:
    if login_time is None:
        return False
    try:
        x = float(login_time)
    except Exception:
        return False
    if x > 1e11:
        x /= 1000.0
    dt = EPOCH_LOGIN + timedelta(seconds=x)
    return dt >= datetime.now(timezone.utc) - timedelta(days=30 * months)

def parse_asa_stamp(ts: Optional[str]) -> Optional[str]:
    """'YYYY.MM.DD-HH.MM.SS' -> 'YYYY-MM-DD HH:MM:SS'"""
    if not ts:
        return None
    try:
        dt = datetime.strptime(ts, "%Y.%m.%d-%H.%M.%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def is_bionic(class_name: str) -> bool:
    s = class_name or ""
    return ("Bionic" in s) or ("Tek" in s) or ("TEK" in s)

def safe_color_indices(raw: Any, length: int = 6) -> List[Optional[int]]:
    if raw is None:
        return [None] * length
    if isinstance(raw, (list, tuple)):
        vals = list(raw)[:length]
        out: List[Optional[int]] = []
        for v in vals:
            try:
                out.append(int(v))
            except Exception:
                out.append(None)
        return out + [None] * (length - len(out))
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                inner = s[1:-1].strip()
                if not inner:
                    return [None] * length
                parts = [p.strip() for p in inner.split(",")]
                out: List[Optional[int]] = []
                for p in parts[:length]:
                    try:
                        out.append(int(float(p)))
                    except Exception:
                        out.append(None)
                return out + [None] * (length - len(out))
            except Exception:
                return [None] * length
    return [None] * length

def format_gene_traits(raw_traits: Any) -> List[str]:
    if not isinstance(raw_traits, list):
        return []

    formatted_traits: List[str] = []
    for raw_trait in raw_traits:
        formatted_trait = format_gene_trait(raw_trait)
        if formatted_trait:
            formatted_traits.append(formatted_trait)
    return formatted_traits

def format_gene_trait(raw_trait: Any) -> Optional[str]:
    if raw_trait is None:
        return None

    if isinstance(raw_trait, dict):
        trait = (
            raw_trait.get("trait")
            or raw_trait.get("Trait")
            or raw_trait.get("name")
            or raw_trait.get("Name")
            or raw_trait.get("value")
            or raw_trait.get("Value")
        )
        level = raw_trait.get("level", raw_trait.get("Level"))
    else:
        trait = getattr(raw_trait, "trait", raw_trait)
        level = getattr(raw_trait, "level", None)

    if trait is None:
        return None

    trait_name = str(getattr(trait, "name", trait)).strip()
    if not trait_name:
        return None

    match = re.fullmatch(r"(.+)\[(-?\d+)\]", trait_name)
    if match:
        trait_name = match.group(1)
        if level is None:
            level = int(match.group(2))

    if level is None:
        return trait_name

    try:
        return f"{trait_name} (Lvl {int(level) + 1})"
    except (TypeError, ValueError):
        return trait_name

def pad_colors_literal_eval(color_indices: Any, length: int = 6) -> List[Optional[int]]:
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

def resolve_location_xyz_to_map(loc: Any, ark_map: Optional[ArkMap]) -> Tuple[Tuple[float, float], str, str]:
    if not loc:
        return (0.0, 0.0), "", ""
    ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
    if ark_map is None:
        return (0.0, 0.0), ccc, ""
    try:
        coords = loc.as_map_coords(ark_map)
        if coords is not None:
            return (coords.lat, coords.long), ccc, getattr(coords, "sub_map_name", None) or ""
    except Exception:
        pass
    return (0.0, 0.0), ccc, ""

def resolve_location_xyz_to_map_cached(loc: Any, map_params: Optional[MapCoordinateParameters]) -> Tuple[Tuple[float, float], str, str]:
    if not loc:
        return (0.0, 0.0), "", ""
    ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
    if map_params is None:
        return (0.0, 0.0), ccc, ""
    try:
        lat, lon, biom = map_params.transform_to(loc.x, loc.y, loc.z)
        return (lat, lon), ccc, biom or ""
    except Exception:
        return (0.0, 0.0), ccc, ""

def resolve_coords_xyz_to_map(latlon_provider, ark_map: Optional[ArkMap]) -> Tuple[Tuple[float, float], str, str]:
    return resolve_location_xyz_to_map(getattr(latlon_provider, "location", None), ark_map)

def wild_within_caps(dino_class: str, level: Optional[int], cap_normal: int, cap_bionic: int) -> bool:
    if level is None:
        return False
    return level <= (cap_bionic if is_bionic(dino_class) else cap_normal)

def json_default(o: Any):
    if isinstance(o, (UUID, Path)):
        return str(o)
    return str(o)

def asv_class_name(obj: Any) -> str:
    short_name = obj.get_short_name() if hasattr(obj, "get_short_name") else None
    return f"{short_name}_C" if short_name else ""

def debug_dump_property_container(label: str, container: Any) -> None:
    print(f"[DEBUG][tamed] {label}", flush=True)
    props = getattr(container, "properties", None)
    if not props:
        print("  <no properties>", flush=True)
        return

    for index, prop in enumerate(props):
        prop_dump = {
            "index": index,
            "name": getattr(prop, "name", None),
            "type": getattr(prop, "type", None),
            "value": getattr(prop, "value", None),
        }
        print(json.dumps(prop_dump, indent=2, default=json_default), flush=True)

def debug_dump_tamed_dino(loop_dino_id: Any, dino: Any) -> None:
    dino_json = dino.to_json_obj()
    dino_obj = getattr(dino, "object", None)
    stats_obj = getattr(getattr(dino, "stats", None), "object", None)
    cryopod = getattr(dino, "cryopod", None)
    cryopod_obj = getattr(cryopod, "object", None)

    summary = {
        "loop_dino_id": str(loop_dino_id),
        "dino_uuid": str(getattr(dino, "uuid", "")),
        "type": type(dino).__name__,
        "short_name": dino.get_short_name() if hasattr(dino, "get_short_name") else None,
        "tamed_name": getattr(dino, "tamed_name", None),
        "blueprint": getattr(dino_obj, "blueprint", None),
        "is_female_attr": getattr(dino, "is_female", None),
        "bIsFemale_property": dino_obj.get_property_value("bIsFemale", None) if dino_obj else None,
        "bIsFemale_json": dino_json.get("bIsFemale"),
        "gender_from_attr": "Female" if getattr(dino, "is_female", False) else "Male",
        "is_cryopodded": getattr(dino, "is_cryopodded", None),
        "cryopod_uuid": str(getattr(cryopod, "uuid", "")) if cryopod else None,
        "cryopod_blueprint": getattr(cryopod_obj, "blueprint", None),
        "cryopod_owner_inv_uuid": str(getattr(cryopod, "owner_inv_uuid", "")) if cryopod else None,
    }

    print("[DEBUG][tamed] SUMMARY", flush=True)
    print(json.dumps(summary, indent=2, default=json_default), flush=True)
    print("[DEBUG][tamed] DINO JSON", flush=True)
    print(json.dumps(dino_json, indent=2, default=json_default), flush=True)
    debug_dump_property_container("DINO OBJECT PROPERTIES", dino_obj)
    debug_dump_property_container("STATUS OBJECT PROPERTIES", stats_obj)

def resolve_dino_sex(dino: Any, dino_class: str) -> str:
    override = DINO_CLASS_SEX_OVERRIDES.get(dino_class)
    if override is not None:
        return override
    return "Female" if getattr(dino, "is_female", False) else "Male"

def get_nested_property(container: Any, name: str, default: Any = None) -> Any:
    if not hasattr(container, "properties"):
        return default

    for prop in container.properties:
        if prop.name == name:
            return prop.value
    return default

def get_wrapped_game_object(obj: Any) -> Any:
    return getattr(obj, "object", obj)

def get_inventory_uuid_from_object(obj: Any) -> Optional[UUID]:
    inventory_ref = obj.get_property_value("MyInventoryComponent") if obj is not None else None
    inventory_uuid = getattr(inventory_ref, "value", inventory_ref)
    if not inventory_uuid:
        return None
    try:
        return UUID(str(inventory_uuid))
    except (TypeError, ValueError):
        return None

def get_market_sell_orders(structure: Any) -> Dict[str, Dict[str, Any]]:
    orders_by_item_uuid: Dict[str, Dict[str, Any]] = {}
    structure_obj = get_wrapped_game_object(structure)
    if structure_obj is None:
        return orders_by_item_uuid

    trade_data = structure_obj.get_property_value("MyTradeData")
    sell_orders = get_nested_property(trade_data, "SellOrders")
    if not hasattr(sell_orders, "properties"):
        return orders_by_item_uuid

    for order in sell_orders.properties:
        order_data = order.value
        item_ref = get_nested_property(order_data, "OrderItemRef")
        item_uuid = getattr(item_ref, "value", None)
        if not item_uuid:
            continue

        orders_by_item_uuid[str(item_uuid)] = {
            "seller": get_nested_property(order_data, "OwnerName"),
            "price_per_unit": get_nested_property(order_data, "PricePerUnit"),
        }

    return orders_by_item_uuid

def format_structure_inventory_items(inventory_items: List[Any], sell_orders: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for item in inventory_items:
        item_obj = getattr(item, "object", None)
        item_uuid = str(getattr(item_obj, "uuid", ""))
        sell_order = sell_orders.get(item_uuid, {})
        price_per_unit = sell_order.get("price_per_unit")
        items.append(
            {
                "id": item_uuid,
                "item": asv_class_name(item),
                "quantity": int(getattr(item, "quantity", 1) or 1),
                "seller": sell_order.get("seller"),
                "price_per_unit": price_per_unit,
                "price_unit": "Hexagon" if price_per_unit is not None else None,
                "blueprint": getattr(item_obj, "blueprint", "") or "",
            }
        )
    return items

def export_structure_inventory_items(structure: Any) -> List[Dict[str, Any]]:
    if not isinstance(structure, StructureWithInventory):
        return []

    try:
        inventory = structure.inventory
        if inventory is None or getattr(inventory, "object", None) is None:
            return []
        inventory_items = list(inventory.items.values())
    except Exception:
        return []

    sell_orders = get_market_sell_orders(structure)
    return format_structure_inventory_items(inventory_items, sell_orders)

def export_structure_inventory_items_from_object(save: AsaSave, structure_obj: Any) -> List[Dict[str, Any]]:
    inventory_uuid = get_inventory_uuid_from_object(structure_obj)
    if inventory_uuid is None:
        return []

    try:
        inventory = Inventory(inventory_uuid, save=save)
        if inventory is None or getattr(inventory, "object", None) is None:
            return []
        inventory_items = list(inventory.items.values())
    except Exception:
        return []

    sell_orders = get_market_sell_orders(structure_obj)
    return format_structure_inventory_items(inventory_items, sell_orders)

# ---------- Exporter: Players ----------

def export_players(
    save: AsaSave,
    export_folder: Path,
    save_path: Path,
    output_modes: Optional[set[str]] = None,
    serverkey: Optional[str] = None,
    db_options: Optional[Dict[str, Any]] = None,
    debug_modes: Optional[set[str]] = None,
) -> Tuple[str, int]:
    output_modes = output_modes or {"json"}
    player_api = PlayerApi(save)

    # Tribe-Namen map
    tribes_by_id: Dict[int, str] = {}
    for tribe in getattr(player_api, "tribes", []):
        try:
            tid = getattr(tribe, "tribe_id", None)
            name = getattr(tribe, "name", None) or getattr(tribe, "tribe_name", None) or ""
            if (tid is None or not name) and hasattr(tribe, "to_json_obj"):
                tj = tribe.to_json_obj() or {}
                tid = tid if tid is not None else tj.get("TribeID")
                name = name or tj.get("TribeName", "")
            if tid is not None:
                tribes_by_id[int(tid)] = str(name or "")
        except Exception:
            continue

    players: List[Dict[str, Any]] = []
    map_folder, map_key = get_map_key_from_savepath(save_path)
    ark_map = MAP_NAME_MAPPING.get(map_key)
    if ark_map is None:
        raise ValueError(f"Unknown map key '{map_key}' for players export")
    map_params = MapCoordinateParameters(ark_map)

    for p in getattr(player_api, "players", []):
        if p.tribe is None:
            continue

        lat = 0.0
        lon = 0.0
        ccc = ""
        loc = p.location
        if loc is not None:
            (lat, lon), ccc, _ = resolve_location_xyz_to_map_cached(loc, map_params)

        entry = {
            "playerid": str(p.id_),
            "steam": p.name,
            "name": p.char_name,
            "tribeid": p.tribe,
            "tribe": tribes_by_id.get(p.tribe),
            "sex": "Female" if p.config.is_female else "Male",
            "lvl": p.stats.level,
            "lat": lat,
            "lon": lon,
            "hp": p.stats.stats.health,
            "stam": p.stats.stats.stamina,
            "melee": p.stats.stats.melee_damage,
            "weight": p.stats.stats.weight,
            "speed": p.stats.stats.movement_speed,
            "food": p.stats.stats.food,
            "water": p.stats.stats.water,
            "oxy": p.stats.stats.oxygen,
            "craft": p.stats.stats.crafting_speed,
            "fort": p.stats.stats.fortitude,
#             "active": is_active_within_months(p.login_time, months=1),
#             "last_login": asa_login_to_mysql_local(p.login_time, tz_name="Europe/Berlin"),
#             "last_login_d": p.login_time,
            "ccc": ccc,
            "steamid": str(p.unique_id),
            "ip": p.ip_address,
            "achievements": [],
            "inventory": [],
            "deaths": int(p.nr_of_deaths),
            # "last_death": p.last_time_died,
        }
        players.append(entry)

    payload = {"map": map_folder, "data": players}
    path = export_folder / "Players.json"
    if "json" in output_modes:
        json_started = time()
        atomic_write_json(payload, path, export_folder)
        perf_log(debug_modes, "players", "write json", json_started, len(players))
    if "db" in output_modes:
        if not serverkey or db_options is None:
            raise ValueError("DB Export für players benötigt serverkey und db_options")
        write_players_mariadb(payload, serverkey, db_options, debug_modes)
    return ("Players.json", len(players))

# ---------- Exporter: Structures ----------

def export_structures(
    save: AsaSave,
    export_folder: Path,
    save_path: Path,
    output_modes: Optional[set[str]] = None,
    serverkey: Optional[str] = None,
    db_options: Optional[Dict[str, Any]] = None,
    debug_modes: Optional[set[str]] = None,
) -> Tuple[str, int]:
    output_modes = output_modes or {"json"}
    structure_api = StructureApi(save)
    map_folder, map_key = get_map_key_from_savepath(save_path)
    ark_map = MAP_NAME_MAPPING.get(map_key)
    map_params = MapCoordinateParameters(ark_map) if ark_map else None

    objects_started = time()
    structure_objects = structure_api.get_all_objects()
    perf_log(debug_modes, "structures", "get_all_objects", objects_started, len(structure_objects))

    out: List[Dict[str, Any]] = []
    inventory_out: List[Dict[str, Any]] = []
    payload_started = time()
    for structure_obj in structure_objects.values():
        owner_name = structure_obj.get_property_value("OwnerName")
        if owner_name is None:
            continue
        tribe_id = structure_obj.get_property_value("TargetingTeam")
        if tribe_id is None:
            continue

        structure_name = structure_obj.get_property_value("BoxName")
        created = parse_asa_stamp(structure_obj.get_property_value("OriginalPlacedTimeStamp", 0))
        (lat, lon), ccc, biom = resolve_location_xyz_to_map_cached(getattr(structure_obj, "location", None), map_params)
        structure_id = str(structure_obj.uuid)
        structure_class = asv_class_name(structure_obj)

        entry = {
            "id": structure_id,
            "tribeid": tribe_id,
            "tribe": owner_name,
            "struct": structure_class,
            "name": structure_name,
            "lat": lat,
            "lon": lon,
            "ccc": ccc,
            "created": created,
            "inventory": [],
        }
        if ark_map == ArkMap.GENESIS1:
            entry["biom"] = biom

        out.append(entry)

        if structure_class in STRUCTURE_INVENTORY_EXPORT_CLASSES:
            inventory_entry = {
                "id": structure_id,
                "tribeid": tribe_id,
                "tribe": owner_name,
                "struct": structure_class,
                "name": structure_name,
                "items": export_structure_inventory_items_from_object(save, structure_obj),
            }
            if ark_map == ArkMap.GENESIS1:
                inventory_entry["biom"] = biom
            inventory_out.append(inventory_entry)
    perf_log(debug_modes, "structures", "build payload", payload_started, len(out))

    payload = {"map": map_folder, "data": out}
    path = export_folder / "Structures.json"

    inventory_payload = {"map": map_folder, "data": inventory_out}
    inventory_path = export_folder / "StructuresInventory.json"
    if "json" in output_modes:
        json_started = time()
        atomic_write_json(payload, path, export_folder)
        atomic_write_json(inventory_payload, inventory_path, export_folder)
        perf_log(debug_modes, "structures", "write json", json_started, len(out))
    if "db" in output_modes:
        if not serverkey or db_options is None:
            raise ValueError("DB Export für structures benötigt serverkey und db_options")
        write_structures_mariadb(payload, inventory_payload, serverkey, db_options, debug_modes)
    return ("Structures.json", len(out))

# ---------- Hilfsfunktionen (Tamed) ----------

def _tamed_owner_field(dino: Any, field: str) -> Optional[Any]:
    try:
        if not getattr(dino, "is_cryopodded", False) and getattr(dino, "owner", None):
            return getattr(dino.owner, field, None)
        cryo_owner = getattr(getattr(getattr(dino, "cryopod", None), "dino", None), "owner", None)
        return getattr(cryo_owner, field, None) if cryo_owner else None
    except Exception:
        return None

def _tamed_location(dino: Any) -> Optional[Any]:
    if not getattr(dino, "is_cryopodded", False):
        return getattr(dino, "location", None)
    cryo_dino = getattr(getattr(dino, "cryopod", None), "dino", None)
    return getattr(cryo_dino, "location", None)

def _extract_added_stat_values(stat_string: str) -> Dict[str, int]:
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

def _dino_property(dino: Any, name: str, default: Any = None) -> Any:
    obj = getattr(dino, "object", None)
    if obj is None:
        return default
    return obj.get_property_value(name, default)

def _dino_blueprint(dino: Any) -> str:
    return getattr(getattr(dino, "object", None), "blueprint", "") or ""

def _dino_class_name(dino: Any) -> str:
    dino_class_short = getattr(dino, "tamed_name", "") or ""
    blueprint = _dino_blueprint(dino)
    return blueprint.split(".")[-1] or dino_class_short

def _dino_color_set_indices(dino: Any) -> List[Optional[int]]:
    if hasattr(dino, "get_color_set_indices"):
        return dino.get_color_set_indices()
    return []

def _dino_gene_traits(dino: Any) -> List[str]:
    gene_traits = getattr(dino, "gene_traits", None)
    if gene_traits is None:
        return []
    return [str(trait) for trait in gene_traits]

def _dino_stat_values(dino: Any) -> str:
    stat_values = getattr(getattr(dino, "stats", None), "stat_values", None)
    if stat_values is None:
        return ""
    return stat_values.to_string_all()

def build_tamed_reader_config(with_cryo: bool) -> GameObjectReaderConfiguration:
    property_names = ["TamedTimeStamp", "TamingTeamID"]
    if with_cryo:
        property_names.append("CustomItemDatas")

    return GameObjectReaderConfiguration(
        blueprint_name_filter=lambda name: name is not None and DinoApi.is_applicable_bp(name),
        property_names=property_names,
    )

def get_all_tamed_narrow(dino_api: DinoApi, with_cryo: bool) -> Dict[UUID, TamedDino]:
    dinos = dino_api.get_all(
        config=build_tamed_reader_config(with_cryo),
        include_cryos=with_cryo,
        include_wild=False,
        include_tamed=True,
        include_babies=True,
    )
    tamed = {key: dino for key, dino in dinos.items() if isinstance(dino, TamedDino)}
    if with_cryo:
        return tamed
    return {key: dino for key, dino in tamed.items() if getattr(dino, "cryopod", None) is None}

# ---------- Exporter: Tamed ----------
def export_tamed(
    save: AsaSave,
    export_folder: Path,
    save_path: Path,
    with_cryo: bool,
    output_modes: Optional[set[str]] = None,
    serverkey: Optional[str] = None,
    db_options: Optional[Dict[str, Any]] = None,
    debug_modes: Optional[set[str]] = None,
) -> Tuple[str, int]:
    export_started = time()
    output_modes = output_modes or {"json"}
    dino_api = DinoApi(save)

    # Read all possible cryopod storages to override later the right tribe_id (transfer-bug) and coords
    storage_started = time()
    structure_api = StructureApi(save)
    #possible_cryopod_storages = ['CryoFridge_C', 'CryoHospital_Base_C', 'IceBox_C', 'StorageBox_Large_C', 'LinkedStorage_C', 'StorageBox_Small_C', 'StorageBox_Huge_C']
    possible_cryopod_storages = ['CryoFridge_C', 'CryoHospital_Base_C']
    config = GameObjectReaderConfiguration(blueprint_name_filter=lambda name: name is not None and any(cls in name for cls in possible_cryopod_storages))

#     config = GameObjectReaderConfiguration(
#         blueprint_name_filter=lambda name: name is not None and (
#             any(s in name for s in {"CryoFridge_C", "CryoHospital_Base_C"}) or
#             any(c in name for c in {"PrimalItem_WeaponEmptyCryopod_C"})
#         ),
#         property_names=["OwnerName", "TargetingTeam", "OriginalPlacedTimeStamp", "BoxName", "InventoryUUID"]
#     )

    storages = structure_api.get_all(config)
    perf_log(debug_modes, "tamed", "cryopod storage scan", storage_started, len(storages))

    inventory_map_started = time()
    inventory_map: Dict[UUID, Dict[str, Any]] = {}
    for key, storage in storages.items():
        if not isinstance(storage, StructureWithInventory):
            continue

        if storage.owner.tribe_id is not None and storage.owner.properties.location is not None:
            inventory_map[storage.inventory_uuid] = {
                "tribe_id": storage.owner.tribe_id,
                "location": storage.owner.properties.location,
            }
    perf_log(debug_modes, "tamed", "cryopod inventory map", inventory_map_started, len(inventory_map))

    map_folder = save_path.parent.name
    map_key = save_path.stem
    ark_map = MAP_NAME_MAPPING.get(map_key)
    if ark_map is None:
        raise ValueError(f"Unknown map key '{map_key}' for tamed export")
    map_params = MapCoordinateParameters(ark_map)

    tamed_out: List[Dict[str, Any]] = []

    # mit/ohne Cryo je nach Flag
    api_started = time()
    all_tamed = get_all_tamed_narrow(dino_api, with_cryo)
    perf_log(debug_modes, "tamed", "dino_api.get_all_tamed_narrow", api_started, len(all_tamed))

    payload_started = time()
    payload_timings: Optional[Dict[str, float]] = {} if perf_enabled(debug_modes) else None
    for dino_id, dino in all_tamed.items():
        segment_started = time()
        if not isinstance(dino, (TamedDino, TamedBaby)):
            perf_add(payload_timings, "type_filter", segment_started)
            continue

        dino_class = _dino_class_name(dino)

        is_cryo = bool(getattr(dino, "is_cryopodded", False))
        perf_add(payload_timings, "class_and_flags", segment_started)

        # Position (keine Weltposition bei Cryo)
        segment_started = time()
        loc = None if is_cryo else _tamed_location(dino)
        ccc, lat, lon, biom = "", 0.0, 0.0, ""
        if loc is not None:
            (lat, lon), ccc, biom = resolve_location_xyz_to_map_cached(loc, map_params)
        perf_add(payload_timings, "location", segment_started)

        segment_started = time()
        tribe_id = _tamed_owner_field(dino, "tamer_tribe_id")
        tamer_name = _tamed_owner_field(dino, "tamer_string")
        targeting_team = _dino_property(dino, "TargetingTeam")
        if (tribe_id == 2000000000 and targeting_team) or tribe_id is None:
            tribe_id = targeting_team
        perf_add(payload_timings, "owner", segment_started)

        # Override tribe_id if the dino was transferred
        segment_started = time()
        if(is_cryo):
            if dino.cryopod.owner_inv_uuid and dino.cryopod.owner_inv_uuid in inventory_map:
                map_entry = inventory_map[dino.cryopod.owner_inv_uuid]
                tribe_id = map_entry["tribe_id"]
                loc = map_entry["location"]

                if loc is not None:
                    (lat, lon), ccc, biom = resolve_location_xyz_to_map_cached(loc, map_params)
        perf_add(payload_timings, "cryo_override", segment_started)

        # Stats (wild/tamed/mut)
        segment_started = time()
        stats_entry: Dict[str, int] = {}
        for prefix, field in STAT_NAME_MAP.items():
            base = getattr(getattr(getattr(dino, "stats", None), "base_stat_points", None), field, 0)
            add = getattr(getattr(getattr(dino, "stats", None), "added_stat_points", None), field, 0)
            mut = getattr(getattr(getattr(dino, "stats", None), "mutated_stat_points", None), field, 0)
            stats_entry[f"{prefix}-w"] = int(base or 0)
            stats_entry[f"{prefix}-t"] = int(add or 0)
            stats_entry[f"{prefix}-m"] = int(mut or 0)
        perf_add(payload_timings, "stats", segment_started)

        segment_started = time()
        c0, c1, c2, c3, c4, c5 = pad_colors_literal_eval(_dino_color_set_indices(dino))

        extracted_traits = format_gene_traits(_dino_gene_traits(dino))
        perf_add(payload_timings, "colors_traits", segment_started)

        segment_started = time()
        tribe_name = _dino_property(dino, "TribeName", "") or ""
        imprinter = _tamed_owner_field(dino, "imprinter") or ""
        imprint = float(getattr(dino, "percentage_imprinted", 0.0) or 0.0)
        tamed_name = getattr(dino, "tamed_name", "") or ""
        sex = resolve_dino_sex(dino, dino_class)
        dino_stats = getattr(dino, "stats", None)
        base_level = getattr(dino_stats, "base_level", None)
        current_level = getattr(dino_stats, "current_level", None)
        maturation = float(getattr(dino, "percentage_matured", 100.0)) if isinstance(dino, TamedBaby) else "100"
        tamed_at_time = parse_asa_stamp(_dino_property(dino, "TamedTimeStamp"))
        mut_f = _dino_property(dino, "RandomMutationsFemale")
        mut_m = _dino_property(dino, "RandomMutationsMale")
        perf_add(payload_timings, "entry_properties", segment_started)

        segment_started = time()
        is_wild_tamed_value = bool(is_wild_tamed(dino))
        perf_add(payload_timings, "is_wild_tamed", segment_started)

        entry: Dict[str, Any] = {
            "id": str(dino_id),
            "tribeid": tribe_id,
            "tribe": tribe_name,
            "tamer": tamer_name or "",
            "imprinter": imprinter,
            "imprint": imprint,
            "creature": dino_class,
            "name": tamed_name,
            "sex": sex,
            "base": base_level,
            "lvl": current_level,
            "lat": lat,
            "lon": lon,
            "biom": biom,
            "cryo": is_cryo,
            "ccc": ccc,
            "isMating": False,
            "isNeutered": False,
            "isClone": False,
            "maturation": maturation,
            "traits": ", ".join(extracted_traits) if extracted_traits else [],
            "inventory": [],
            "is_wild_tamed": is_wild_tamed_value,
            "tamedAtTime": tamed_at_time,
            "mut-f": mut_f,
            "mut-m": mut_m,
            "c0": c0, "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
        }
        entry.update(stats_entry)

        segment_started = time()
        stat_values = _dino_stat_values(dino)
        if stat_values:
            entry.update(_extract_added_stat_values(stat_values))
        perf_add(payload_timings, "added_stat_values", segment_started)

        tamed_out.append(entry)
    perf_log(debug_modes, "tamed", "build payload", payload_started, len(tamed_out))
    perf_log_breakdown(debug_modes, "tamed", "build payload", payload_timings)

    payload = {"map": map_folder, "data": tamed_out}
    path = export_folder / "TamedDinos.json"
    if "json" in output_modes:
        json_started = time()
        atomic_write_json(payload, path, export_folder)
        perf_log(debug_modes, "tamed", "write json", json_started, len(tamed_out))
    if "db" in output_modes:
        if not serverkey or db_options is None:
            raise ValueError("DB Export für tamed benötigt serverkey und db_options")
        write_tamed_mariadb(payload, serverkey, db_options, debug_modes)
    perf_log(debug_modes, "tamed", "total export_tamed", export_started, len(tamed_out))
    return ("TamedDinos.json", len(tamed_out))

# ---------- Exporter: Wild ----------

def export_wild(save: AsaSave, export_folder: Path, save_path: Path, cap_normal: int, cap_bionic: int) -> Tuple[str, int]:
    TRASH_DINOS = {
        'Coel_Character_BP_C',
        'Ant_Character_BP_C',
        'Salmon_Character_BP_C',
        'Piranha_Character_BP_C',
        'Dragonfly_Character_BP_C',
        'FlyingAnt_Character_BP_C',
        'Jugbug_Water_Character_BP_C',
        'Jugbug_Oil_Character_BP_C'
    }

    dino_api = DinoApi(save)

    # Für "map" im Payload: server_folder (= Elternordner mit *_a), fallback map_folder
    server_folder = None
    for p in save_path.parents:
        if p.name.endswith("_a"):
            server_folder = p.name
            break
    if server_folder is None:
        server_folder = save_path.parent.name

    map_key = save_path.stem
    ark_map = MAP_NAME_MAPPING.get(map_key)
    map_params = MapCoordinateParameters(ark_map) if ark_map else None

    out: List[Dict[str, Any]] = []
    for dino_id, dino in dino_api.get_all_wild_tamables().items():
        if not isinstance(dino, Dino):
            continue

        lvl = dino.stats.base_level if dino.stats else None
        dino_class = _dino_class_name(dino)

        if dino_class in TRASH_DINOS:
            continue
        if "_Corrupt" in dino_class:
            continue
        if not wild_within_caps(dino_class, lvl, cap_normal, cap_bionic):
            continue

        (lat, lon), ccc, biom = resolve_location_xyz_to_map_cached(getattr(dino, "location", None), map_params)
        coords = (lat, lon)

        s = dino.stats
        colors = safe_color_indices(_dino_color_set_indices(dino))
        try:
            int_id = int(str(dino_id))
            int_id = int_id if -(2**63) <= int_id < 2**63 else None
        except Exception:
            int_id = None

        extracted_traits = format_gene_traits(_dino_gene_traits(dino))

        out.append(
            {
                "id": int_id if int_id is not None else str(dino_id),
                "creature": dino_class,
                "sex": resolve_dino_sex(dino, dino_class),
                "lvl": (s.base_level if s else None),
                "lat": coords[0],
                "lon": coords[1],
                "biom": biom,
                "hp": int(getattr(getattr(s, "base_stat_points", None), "health", 0) or 0),
                "stam": int(getattr(getattr(s, "base_stat_points", None), "stamina", 0) or 0),
                "melee": int(getattr(getattr(s, "base_stat_points", None), "melee_damage", 0) or 0),
                "weight": int(getattr(getattr(s, "base_stat_points", None), "weight", 0) or 0),
                "speed": int(getattr(getattr(s, "base_stat_points", None), "movement_speed", 0) or 0),
                "food": int(getattr(getattr(s, "base_stat_points", None), "food", 0) or 0),
                "oxy": int(getattr(getattr(s, "base_stat_points", None), "oxygen", 0) or 0),
                "craft": int(getattr(getattr(s, "base_stat_points", None), "crafting_speed", 0) or 0),
                "c0": colors[0],
                "c1": colors[1],
                "c2": colors[2],
                "c3": colors[3],
                "c4": colors[4],
                "c5": colors[5],
                "ccc": ccc,
                "tameable": True,
                "traits": ", ".join(extracted_traits) if extracted_traits else []
            }
        )

    payload = {"map": server_folder, "data": out}
    path = export_folder / "WildDinos.json"
    atomic_write_json(payload, path, export_folder)
    return ("WildDinos.json", len(out))

# ---------- Typen/Prio ----------

def parse_types(type_arg: str) -> List[str]:
    t = (type_arg or "").strip().lower()
    if not t:
        raise ValueError("--type darf nicht leer sein")
    if t == "all":
        return sorted(SUPPORTED_TYPES)
    parts = [p.strip() for p in t.split(",") if p.strip()]
    unknown = [p for p in parts if p not in SUPPORTED_TYPES]
    if unknown:
        raise ValueError(f"Unbekannte Typen in --type: {', '.join(unknown)}. Erlaubt: {', '.join(sorted(SUPPORTED_TYPES))} oder 'all'.")
    # Reihenfolge beibehalten, Duplikate entfernen
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            out.append(p)
            seen.add(p)
    return out

def prioritize_types(types: List[str]) -> List[str]:
    """
    Priorität: 'tamed' zuerst, 'structures' als zweites (falls jeweils gesetzt),
    die restlichen folgen in der ursprünglichen Reihenfolge.
    """
    out: List[str] = []
    if "tamed" in types:
        out.append("tamed")
    if "structures" in types:
        out.append("structures")
    for t in types:
        if t not in ("tamed", "structures"):
            out.append(t)
    return out

# ---------- Child-Worker (eigener Prozess) ----------

def child_worker(
    t: str,
    save_path: Path,
    export_folder: Path,
    max_level: int,
    max_level_bionic: int,
    with_cryo_flag: int,
    output_modes: set[str],
    serverkey: str,
    db_options: Optional[Dict[str, Any]],
    debug_modes: set[str],
    result_q: mp.Queue,
):
    """
    Läuft in einem separaten Prozess:
      - öffnet ein eigenes AsaSave
      - führt genau EINEN Export aus
      - legt Ergebnis/Fehler ins result_q
    Hinweis: with_cryo_flag wirkt NUR bei tamed, ansonsten ignoriert.
    """
    t0 = time()
    try:
        export_folder.mkdir(parents=True, exist_ok=True)
        save_started = time()
        save = AsaSave(save_path)
        perf_log(debug_modes, t, "load AsaSave", save_started)

        if t == "tamed":
            fname, cnt = export_tamed(save, export_folder, save_path, bool(with_cryo_flag), output_modes, serverkey, db_options, debug_modes)
        elif t == "players":
            fname, cnt = export_players(save, export_folder, save_path, output_modes, serverkey, db_options, debug_modes)
        elif t == "structures":
            fname, cnt = export_structures(save, export_folder, save_path, output_modes, serverkey, db_options, debug_modes)
        elif t == "wild":
            fname, cnt = export_wild(save, export_folder, save_path, max_level, max_level_bionic)
        else:
            raise ValueError(f"Unsupported export type: {t}")
        elapsed = time() - t0
        target = describe_export_target(t, fname, export_folder, output_modes, db_options)
        result_q.put({"type": t, "ok": True, "file": target, "count": cnt, "elapsed": elapsed, "error": None})
    except Exception as e:
        elapsed = time() - t0
        result_q.put({"type": t, "ok": False, "file": None, "count": 0, "elapsed": elapsed, "error": str(e)})

# ---------- Main ----------

def main() -> None:
    global_start = time()
    args = build_argparser().parse_args()

    if not args.savegame.exists():
        raise FileNotFoundError(f"Savegame nicht gefunden: {args.savegame}")

    requested = parse_types(args.type)
    requested = prioritize_types(requested)
    output_modes = parse_output_modes(args.output_mode)
    debug_modes = parse_debug_modes(args.debug)
    validate_output_modes(requested, output_modes)
    needs_db = "db" in output_modes and any(t in DB_SUPPORTED_TYPES for t in requested)
    db_options = load_db_options(args.db_config) if needs_db else None
    export_folder = ensure_export_folder(args.output, args.serverkey)
    save_path = args.savegame

    results: List[Tuple[str, int]] = []

    if args.parallel == 1 and len(requested) > 1:
        # Paralleler Modus: Einmal-Prozesse, die sich nach Fertigstellung direkt beenden
        ctx = get_mp_context()
        result_q: mp.Queue = ctx.Queue()

        # Prozesse in priorisierter Reihenfolge starten
        procs: List[mp.Process] = []
        for t in requested:
            p = ctx.Process(
                target=child_worker,
                args=(t, save_path, export_folder, args.max_level, args.max_level_bionic, args.withcryo,
                      output_modes, args.serverkey, db_options, debug_modes, result_q),
            )
            p.start()
            procs.append(p)

        finished = 0
        total = len(procs)
        while finished < total:
            msg = result_q.get()  # blockiert bis ein Ergebnis kommt
            t = msg["type"]
            if msg["ok"]:
                results.append((str(msg["file"]), msg["count"]))
                print(f"[OK][{t}] Wrote {msg['count']:>6} entries in {msg['elapsed']:.2f} secs -> {msg['file']}")
            else:
                print(f"[ERR][{t}] in {msg['elapsed']:.2f} secs -> {msg['error']}")
            finished += 1

        # Aufräumen (sicherstellen, dass alle Prozesse beendet sind)
        for p in procs:
            p.join()

    else:
        # Seriell: Save einmal laden und wiederverwenden (ressourcenschonend)
        save_started = time()
        save = AsaSave(save_path)
        perf_log(debug_modes, "main", "load AsaSave", save_started)

        for t in requested:
            t0 = time()
            if t == "tamed":
                res = export_tamed(save, export_folder, save_path, bool(args.withcryo), output_modes, args.serverkey, db_options, debug_modes)
            elif t == "structures":
                res = export_structures(save, export_folder, save_path, output_modes, args.serverkey, db_options, debug_modes)
            elif t == "players":
                res = export_players(save, export_folder, save_path, output_modes, args.serverkey, db_options, debug_modes)
            elif t == "wild":
                res = export_wild(save, export_folder, save_path, args.max_level, args.max_level_bionic)
            else:
                raise ValueError(f"Unsupported export type: {t}")
            elapsed = time() - t0
            target = describe_export_target(t, res[0], export_folder, output_modes, db_options)
            results.append((target, res[1]))
            print(f"[OK][{t}] Wrote {res[1]:>6} entries in {elapsed:.2f} secs -> {target}")

    # Zusammenfassung
    total_entries = sum(c for _, c in results)
    took = time() - global_start
    print(f"Finished {len(results)} export(s), total entries: {total_entries}, runtime: {took:.2f}s")


if __name__ == "__main__":
    mp.freeze_support()
    main()
