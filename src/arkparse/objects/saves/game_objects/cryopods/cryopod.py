import logging
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from io import BytesIO
from zipfile import ZipFile

from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.game_objects import ArkGameObject
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.logging import ArkSaveLogger

from arkparse.utils import WildcardInflaterInputStream

logger = logging.getLogger(__name__)

class Cryopod:
    NAME_CONSTANTS = {
        0: "TribeName",
        1: "StrProperty",
        2: "bServerInitializedDino",
        3: "BoolProperty",
        5: "FloatProperty",
        6: "ColorSetIndices",
        7: "ByteProperty",
        8: "None",
        9: "ColorSetNames",
        10: "NameProperty",
        11: "TamingTeamID",
        12: "UInt64Property",
        13: "RequiredTameAffinity",
        14: "TamingTeamID",
        15: "IntProperty",
        19: "StructProperty",
        23: "DinoID1",
        24: "UInt32Property",
        25: "DinoID2",
        31: "UploadedFromServerName",
        32: "TamedOnServerName",
        36: "TargetingTeam",
        38: "bReplicateGlobalStatusValues",
        39: "bAllowLevelUps",
        40: "bServerFirstInitialized",
        41: "ExperiencePoints",
        42: "CurrentStatusValues",
        44: "ArrayProperty",
        55: "bIsFemale",
    }

    def __init__(self, uuid_: uuid.UUID):
        self.uuid = uuid_
        self.dino_and_status_component: List['ArkGameObject'] = []
        self.saddle: Optional['ArkPropertyContainer'] = None
        self.costume: Optional['ArkPropertyContainer'] = None

    def parse_dino_and_status_component_data(self, data: bytes, reader_config: 'GameObjectReaderConfiguration'):
        try:
            with BytesIO(data) as raw_input_stream, \
                 ZipFile(raw_input_stream) as inflater_input_stream, \
                 WildcardInflaterInputStream(inflater_input_stream) as input_stream:

                self.read_header_dino_and_status_component(raw_input_stream, input_stream, reader_config)
        except Exception as e:
            logger.error("Failed to read data for %s", self, exc_info=e)
            if reader_config.throw_exception_on_parse_error:
                raise RuntimeError(f"Failed to read cryopod data for UUID {self.uuid}") from e

    def read_header_dino_and_status_component(self, raw_input_stream, inflated_input_stream, reader_config: 'GameObjectReaderConfiguration'):
        header_data = ArkBinaryParser(raw_input_stream.read(12))
        header_data.validate_int32(0x0406)
        inflated_size = header_data.read_int()  # size of inflated data before processing
        names_offset = header_data.read_int()

        inflated_data = inflated_input_stream.read()
        if reader_config.binary_files_output_directory:
            output_dir = Path(reader_config.binary_files_output_directory) / "cryopods"
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{self.uuid}.bytes0.bin").write_bytes(inflated_data)

        self.read_dino_and_status_component(ArkBinaryParser(inflated_data), names_offset)

    def read_dino_and_status_component(self, reader: 'ArkBinaryParser', names_table_offset: int):
        save_context = reader.save_context
        save_context.names = self.read_name_table(reader, names_table_offset)
        save_context.use_constant_name_table(self.NAME_CONSTANTS)
        save_context.generate_unknown_names = True

        reader.set_position(0)
        self.dino_and_status_component = []

        object_count = reader.read_int()
        for _ in range(object_count):
            game_object = ArkGameObject.read_from_custom_bytes(reader)
            self.dino_and_status_component.append(game_object)

        for game_object in self.dino_and_status_component:
            try:
                if reader.position != game_object.properties_offset:
                    logger.warning("Reader position %d does not match properties offset %d, bytes left: %d",
                                   reader.position, game_object.properties_offset,
                                   game_object.properties_offset - reader.position)
                    reader.set_position(game_object.properties_offset)
                game_object.read_properties(reader)
                game_object.read_extra_data(reader)
                reader.read_int()  # Dummy read to sync

            except Exception as e:
                logger.error("Error reading properties for cryopod %s", self, exc_info=e)
                ArkSaveLogger.enable_debug_logging = True
                reader.set_position(game_object.properties_offset)
                game_object.properties = []
                game_object.read_properties(reader)
                game_object.read_extra_data(reader)
                ArkSaveLogger.enable_debug_logging = False

    @staticmethod
    def read_name_table(reader: 'ArkBinaryParser', names_table_offset: int) -> Dict[int, str]:
        reader.set_position(names_table_offset)
        name_table = {}
        name_count = reader.read_int()
        for i in range(name_count):
            name_table[i | 0x10000000] = reader.read_string()
        return name_table
