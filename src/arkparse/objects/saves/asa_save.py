import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Collection
import uuid

from arkparse.logging import ArkSaveLogger

from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration
from arkparse.parsing.ark_binary_parser import ArkBinaryParser

from .header_location import HeaderLocation
from .game_objects.ark_game_object import ArkGameObject
from .game_objects.ark_game_object import ArkGameObject
from .save_context import SaveContext
from arkparse.utils import TEMP_FILES_DIR

logger = logging.getLogger(__name__)

class AsaSave:
    MAX_IN_LIST = 10000
    nr_parsed = 0
    parsed_objects: Dict[uuid.UUID, ArkGameObject] = {}   

    def __init__(self, ark_file: Path, read_only: bool = True):

        # create temp copy of file
        temp_save_path = TEMP_FILES_DIR / (str(uuid.uuid4()) + ".ark")
        with open(ark_file, 'rb') as file:
            with open(temp_save_path, 'wb') as temp_file:
                temp_file.write(file.read())

        self.sqlite_db = temp_save_path
        self.save_context = SaveContext()
        self.var_objects = {}
        self.var_objects["placed_structs"] = {}
        self.var_objects["g_placed_structs"] = {}

        conn_str = f"file:{temp_save_path}?mode={'ro' if read_only else 'rw'}"
        self.connection = sqlite3.connect(conn_str, uri=True)
        
        self.list_all_items_in_db()
        self.read_header()
        self.read_actor_locations()

    def __del__(self):
        self.close()

        # clean up temp file
        if self.sqlite_db.exists():
            self.sqlite_db.unlink()

    def list_all_items_in_db(self):
        query = "SELECT key, value FROM game"
        with self.connection as conn:
            cursor = conn.execute(query)
            name = cursor.description
            rowCount = 0
            for row in cursor:
                rowCount += 1
            ArkSaveLogger.debug_log("Found %d items in game table", rowCount)

        # get custom values
        query = "SELECT key, value FROM custom"
        with self.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                ArkSaveLogger.debug_log("Custom key: %s", row[0])

    def read_actor_locations(self):
        actor_transforms = self.get_custom_value("ActorTransforms")
        ArkSaveLogger.debug_log("Actor transforms table retrieved")
        if actor_transforms:
            self.save_context.actor_transforms = actor_transforms.read_actor_transforms()   

    def read_header(self):
        header_data = self.get_custom_value("SaveHeader")
                       
        self.save_context.save_version = header_data.read_short()
        ArkSaveLogger.debug_log("Save version: %d", self.save_context.save_version)
        name_table_offset = header_data.read_int()
        ArkSaveLogger.debug_log("Name table offset: %d", name_table_offset)
        self.save_context.game_time = header_data.read_double()
        ArkSaveLogger.debug_log("Game time: %f", self.save_context.game_time)

        if self.save_context.save_version >= 12:
            self.save_context.unknown_value = header_data.read_uint32()
            ArkSaveLogger.debug_log("Unknown value: %d", self.save_context.unknown_value)

        self.save_context.sections = self.read_locations(header_data)
        
        # check_uint64(header_data, 0)
        header_data.set_position(name_table_offset)
        self.save_context.names = self.read_table(header_data)

    def read_table(self, header_data: 'ArkBinaryParser') -> Dict[int, str]:
        count = header_data.read_int()

        result = {}
        for _ in range(count):
            key = header_data.read_uint32()
            result[key] = header_data.read_string()
        return result

    def read_locations(self, header_data: 'ArkBinaryParser') -> list:
        parts = []
        num_parts = header_data.read_uint32()
        for _ in range(num_parts):
            part = header_data.read_string()
            if not part.endswith("_WP"):
                parts.append(HeaderLocation(part))
            header_data.validate_uint32(0xFFFFFFFF)
        return parts
    
    def get_game_obj_binary(self, obj_uuid: uuid.UUID) -> Optional[bytes]:
        query = "SELECT value FROM game WHERE key = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (self.uuid_to_byte_array(obj_uuid),))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Object with UUID {obj_uuid} not found in database")

        return row[0]
    
    def find_value_in_game_table_objects(self, value: bytes):
        query = "SELECT key, value FROM game"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            reader = ArkBinaryParser(row[1], self.save_context)
            result = reader.find_byte_sequence(value)

            for r in result:
                print(f"Found at {row[0]}, index: {r}")

                obj = self.get_game_object_by_id(self.byte_array_to_uuid(row[0]))
                if obj:
                    print(f"Object: {obj.blueprint}")
            
    def find_value_in_custom_tables(self, value: bytes):
        query = "SELECT key, value FROM custom"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            reader = ArkBinaryParser(row[1], self.save_context)
            result = reader.find_byte_sequence(value)

            for r in result:
                print(f"Found at {row[0]}, index: {r}")

    def get_obj_uuids(self) -> Collection[uuid.UUID]:
        query = "SELECT key FROM game"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [self.byte_array_to_uuid(row[0]) for row in cursor]
    
    def print_tables_and_sizes(self):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            table_name = row[0]
            query = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"Table {table_name} has {count} rows")

    def print_custom_table_sizes(self):
        query = "SELECT key, LENGTH(value) FROM custom"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            print(f"Key: {row[0]}, size: {row[1]}")
    
    def is_in_db(self, obj_uuid: uuid.UUID) -> bool:
        query = "SELECT key FROM game WHERE key = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (self.uuid_to_byte_array(obj_uuid),))
        return cursor.fetchone() is not None
        
    def add_obj_to_db(self, obj_uuid: uuid.UUID, obj_data: bytes):
        query = "INSERT INTO game (key, value) VALUES (?, ?)"
        with self.connection as conn:
            conn.execute(query, (self.uuid_to_byte_array(obj_uuid), obj_data))

    def modify_obj_in_db(self, obj_uuid: uuid.UUID, obj_data: bytes):
        query = "UPDATE game SET value = ? WHERE key = ?"
        with self.connection as conn:
            conn.execute(query, (obj_data, self.uuid_to_byte_array(obj_uuid)))

    def remove_obj_from_db(self, obj_uuid: uuid.UUID):
        query = "DELETE FROM game WHERE key = ?"
        with self.connection as conn:
            conn.execute(query, (self.uuid_to_byte_array(obj_uuid),))

    def add_new_actor_transform_to_db(self, uuid: uuid.UUID, binary_data: bytes):
        actor_transforms = self.get_custom_value("ActorTransforms")

        if actor_transforms:
            actor_transforms.set_position(actor_transforms.size() - 16)
            actor_transforms.insert_bytes(self.uuid_to_byte_array(uuid))
            actor_transforms.set_position(actor_transforms.size() - 16)
            actor_transforms.insert_bytes(binary_data)

            query = "UPDATE custom SET value = ? WHERE key = 'ActorTransforms'"
            with self.connection as conn:
                conn.execute(query, (actor_transforms.byte_buffer,))

    def store_db(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as new_conn:
            self.connection.backup(new_conn)
        
        logger.info(f"Database successfully backed up to {path}")

    def get_game_objects(self, reader_config: GameObjectReaderConfiguration) -> Dict[uuid.UUID, 'ArkGameObject']:
        query = "SELECT key, value FROM game"
        game_objects = {}
        row_index = 0
        objects = []

        ArkSaveLogger.enter_struct("GameObjects")

        with self.connection as conn:   
            cursor = conn.execute(query)
            for row in cursor:
                if row_index < 0:
                    row_index += 1
                    self.nr_parsed += 1
                    continue

                obj_uuid = self.byte_array_to_uuid(row[0])
                self.save_context.all_uuids.append(obj_uuid)
                if reader_config.uuid_filter and not reader_config.uuid_filter(obj_uuid):
                    ArkSaveLogger.debug_log("Skipping object %s", obj_uuid)
                    ArkSaveLogger.exit_struct()
                    continue

                byte_buffer = ArkBinaryParser(row[1], self.save_context)
                ArkSaveLogger.byte_buffer = byte_buffer
                ArkSaveLogger.set_file(byte_buffer, "game_object.bin")
                class_name = byte_buffer.read_name()
                ArkSaveLogger.enter_struct(class_name)

                if reader_config.blueprint_name_filter and not reader_config.blueprint_name_filter(class_name):
                    ArkSaveLogger.exit_struct()
                    continue

                try:
                    if class_name not in objects:
                        objects.append(class_name)
                    
                    if obj_uuid not in self.parsed_objects.keys():
                        ark_game_object = self.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)
                        
                        if ark_game_object:
                            game_objects[obj_uuid] = ark_game_object
                            self.parsed_objects[obj_uuid] = ark_game_object
                    else:
                        game_objects[obj_uuid] = self.parsed_objects[obj_uuid]

                except Exception as e:
                    ArkSaveLogger.enable_debug = True
                    byte_buffer.find_names()
                    raise Exception("Error parsing object %s of type %s: %s", obj_uuid, class_name, exc_info=e)
                
                for object in objects:
                    ArkSaveLogger.debug_log("Object: %s", object)
                ArkSaveLogger.exit_struct()

        for o in self.var_objects:
            sorted_properties = sorted(self.var_objects[o].items(), key=lambda item: item[1], reverse=True)
            for p, count in sorted_properties:
                print("  - " + p + " " + str(count))
        
        return game_objects
    
    def get_all_present_classes(self):
        query = "SELECT value FROM game"
        classes = []
        with self.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                byte_buffer = ArkBinaryParser(row[0], self.save_context)
                class_name = byte_buffer.read_name()
                if class_name not in classes:
                    classes.append(class_name)
        return classes

    def get_game_object_by_id(self, obj_uuid: uuid.UUID) -> Optional['ArkGameObject']:
        bin = self.get_game_obj_binary(obj_uuid)
        reader = ArkBinaryParser(bin, self.save_context)
        obj = ArkGameObject(obj_uuid, reader.read_name(), reader)
        return obj

    def get_custom_value(self, key: str) -> Optional['ArkBinaryParser']:
        query = f"SELECT value FROM custom WHERE key = ? LIMIT 1"
        cursor = self.connection.cursor()
        cursor.execute(query, (key,))
        row = cursor.fetchone()
        if row:
            return ArkBinaryParser(row[0], self.save_context)
        return None

    def close(self):
        if self.connection:
            self.connection.close()

    def remove_leading_slash(self, path: str) -> Path:
        return Path(path.lstrip('/'))

    @staticmethod
    def byte_array_to_uuid(byte_array: bytes) -> uuid.UUID:
        return uuid.UUID(bytes=byte_array)

    @staticmethod
    def uuid_to_byte_array(obj_uuid: uuid.UUID) -> bytes:
        return obj_uuid.bytes
    
    def parse_as_predefined_object(self, obj_uuid, class_name, byte_buffer):
        self.nr_parsed += 1

        if self.nr_parsed % 2500 == 0:
            ArkSaveLogger.debug_log(f"Nr parsed: {self.nr_parsed}")

        skip_list = [
            "/QoLPlus/Items/OmniTool/PrimalItem_OmniTool.PrimalItem_OmniTool_C",
            "/QoLPlus/Items/MultiTool/PrimalItem_SplusMultiTool.PrimalItem_SplusMultiTool_C",
            "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_StartingNote.PrimalItem_StartingNote_C",
            "/Script/ShooterGame.StructurePaintingComponent",
            "/Game/Packs/Frontier/Structures/TreasureCache/TreasureMap/PrimalItem_TreasureMap_WildSupplyDrop.PrimalItem_TreasureMap_WildSupplyDrop_C",
            "/Game/PrimalEarth/Structures/Wooden/CropPlotLarge_SM.CropPlotLarge_SM_C",
            "/Game/PrimalEarth/Structures/Pipes/WaterPipe_Stone_Intake.WaterPipe_Stone_Intake_C",
            "/Game/PrimalEarth/Structures/BuildingBases/WaterTank_Metal.WaterTank_Metal_C",
            "/Game/PrimalEarth/Structures/WaterTap_Metal.WaterTap_Metal_C"
        ]

        if class_name in skip_list:
            return None
    
        return ArkGameObject(obj_uuid, class_name, byte_buffer)
        
