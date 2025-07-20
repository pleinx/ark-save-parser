import logging
import subprocess
from pathlib import Path

from arkparse.utils.temp_files import TEMP_FILES_DIR

class ArkSaveLogger:
    enable_debug = False
    suppress_warnings = True
    current_struct_path = []
    file = ""
    byte_buffer = None
    temp_file_path = TEMP_FILES_DIR
    log_limit = 0
    log_limit_enabled = False

    @staticmethod
    def debug_log(message: str, *args):
        if  ArkSaveLogger.enable_debug and (ArkSaveLogger.log_limit_enabled is False or ArkSaveLogger.log_limit > 0):
            if ArkSaveLogger.log_limit_enabled:
                ArkSaveLogger.log_limit -= 1
            structPath = ""
            for s in ArkSaveLogger.current_struct_path:
                structPath = structPath + f"[{s}]"
            message = structPath + message
            logging.info(message, *args)

    @staticmethod
    def enter_struct(struct_name: str):
        # self.debug_log("Entering struct %s", struct_name)
        ArkSaveLogger.current_struct_path.append(struct_name)

    @staticmethod
    def exit_struct():
        # self.debug_log("Exiting struct %s", self.current_struct_path)
        if len(ArkSaveLogger.current_struct_path) > 0:
            ArkSaveLogger.current_struct_path.pop()

    @staticmethod
    def reset_struct_path():
        ArkSaveLogger.current_struct_path = []

    @staticmethod
    def set_file(reader, name):
        if ArkSaveLogger.temp_file_path != "" and ArkSaveLogger.enable_debug:
            ArkSaveLogger.byte_buffer = reader
            ArkSaveLogger.file = ArkSaveLogger.temp_file_path / name
            with open(ArkSaveLogger.file, 'wb') as file:
                file.write(reader.byte_buffer)

    @staticmethod
    def open_hex_view(wait: bool = False):
        if ArkSaveLogger.enable_debug and ArkSaveLogger.byte_buffer is not None:
            parser = Path(__file__).resolve().parent.parent.parent / 'binary-reader' / 'binary_visualizer.py'
            logging.info("Opening hex view")
            subprocess.Popen(['python', parser, '-f', ArkSaveLogger.file, '-i', str(ArkSaveLogger.byte_buffer.get_position())])
            if wait:
                input("Press Enter to continue...")

# Configure the logger
logging.basicConfig(level=logging.INFO)
ArkSaveLogger.enable_debug = False