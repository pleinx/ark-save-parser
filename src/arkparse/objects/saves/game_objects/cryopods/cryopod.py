import logging
from io import BytesIO
import zlib

from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.game_objects import ArkGameObject
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.logging import ArkSaveLogger

logger = logging.getLogger(__name__)

class Cryopod:
    def __init__(self, uuid, parser: ArkBinaryParser):
        self.uuid = uuid
        self.dinoAndStatusComponent = []
        self.saddle = None
        self.costume = None

    def parseDinoAndStatusComponentData(self, bytes_data: List[int]):
        try:
            raw_input_stream = BytesIO(bytes_data)
            header_data_bytes = raw_input_stream.read(12)
            if len(header_data_bytes) < 12:
                raise ValueError("Insufficient data for header")
            header_data = ArkBinaryParser(header_data_bytes)

            header_data.validate_uint32(0x0406)
            inflated_size = header_data.read_uint32()
            names_offset = header_data.read_uint32()

            compressed_data = raw_input_stream.read()
            if not compressed_data:
                raise ValueError("No compressed data found")

            # Decompress data with error handling
            try:
                inflated_data = zlib.decompress(compressed_data) # decompress the data using the DEFLATE algorithm
            except zlib.error as e:
                raise RuntimeError(f"Failed to decompress cryopod data for UUID {self.uuid}") from e

            inflated_data_reader = ArkBinaryParser(inflated_data)
            ArkSaveLogger.set_file(inflated_data_reader, "debug.bin")
            self.readDinoAndStatusComponent(inflated_data_reader, names_offset)

        except Exception as e:
            raise RuntimeError(f"Failed to read cryopod data for UUID {self.uuid}") from e

    def readDinoAndStatusComponent(self, reader : ArkBinaryParser, names_table_offset : int):
        save_context = reader.save_context
        save_context.names = self.readNameTable(reader, names_table_offset)
        save_context.constant_name_table = self.NAME_CONSTANTS
        save_context.generate_unknown_names = True
        reader.position = 0

        self.dinoAndStatusComponent = []
        object_count = reader.read_uint32()
        for _ in range(object_count):
            game_object = ArkGameObject.readFromCustomBytes(reader)
            self.dinoAndStatusComponent.append(game_object)

        for game_object in self.dinoAndStatusComponent:
            try:
                if reader.getPosition() != game_object.getPropertiesOffset():
                    log.warning(f"Reader position {reader.getPosition()} does not match properties offset {game_object.getPropertiesOffset()}, bytes left to read: {game_object.getPropertiesOffset() - reader.getPosition()}")
                    reader.setPosition(game_object.getPropertiesOffset())
                game_object.readProperties(reader)
                game_object.readExtraData(reader)
                reader.readInt()  # Assuming this is to align or consume extra data
            except Exception as e:
                log.error(f"Error reading properties for cryopod {self}, debug info follows:", exc_info=e)
                ArkSaveUtils.enableDebugLogging = True
                reader.setPosition(game_object.getPropertiesOffset())
                game_object.setProperties([])
                game_object.readProperties(reader)
                game_object.readExtraData(reader)
            finally:
                ArkSaveUtils.enableDebugLogging = False

    def readNameTable(self, reader, names_table_offset):
          
        return name_table
