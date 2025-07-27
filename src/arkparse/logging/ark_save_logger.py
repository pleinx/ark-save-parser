import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

from arkparse.utils.temp_files import read_config_file, write_config_file, TEMP_FILES_DIR

class ArkSaveLogger:
    class LogTypes:
        PARSER = "parser"
        INFO = "info"
        API = "api"
        ERROR = "error"
        DEBUG = "debug"
        WARNING = "warning"
        SAVE = "save"
        ALL = "all"

    class LogColors:
        WHITE = "\033[0m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        RESET = "\033[0m"

    current_struct_path = []
    allow_invalid_objects = False
    _file = ""
    _byte_buffer = None
    _temp_file_path = TEMP_FILES_DIR
    _file_viewer_enabled = True
    _log_level_states = None

    __LOG_CONFIG_FILE_NAME = "logger"

    @staticmethod
    def save_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.SAVE, ArkSaveLogger.LogColors.GREEN)

    @staticmethod
    def parser_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.PARSER, ArkSaveLogger.LogColors.CYAN)

    @staticmethod
    def info_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.INFO, ArkSaveLogger.LogColors.WHITE)

    @staticmethod
    def api_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.API, ArkSaveLogger.LogColors.MAGENTA)

    @staticmethod
    def error_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.ERROR, ArkSaveLogger.LogColors.RED)

    @staticmethod
    def debug_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.DEBUG, ArkSaveLogger.LogColors.BLUE)

    @staticmethod
    def warning_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.WARNING, ArkSaveLogger.LogColors.YELLOW)

    @staticmethod
    def __init_log_levels():
        config = read_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME)
        if config is None:
            ArkSaveLogger._log_level_states = {
                ArkSaveLogger.LogTypes.PARSER: False,
                ArkSaveLogger.LogTypes.INFO: False,
                ArkSaveLogger.LogTypes.API: False,
                ArkSaveLogger.LogTypes.ERROR: False,
                ArkSaveLogger.LogTypes.DEBUG: False,
                ArkSaveLogger.LogTypes.WARNING: False,
                ArkSaveLogger.LogTypes.SAVE: False,
                "all": False
            }
            write_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME, ArkSaveLogger._log_level_states)
        else:
            ArkSaveLogger._log_level_states = config
        
    @staticmethod
    def __log(message: str, log_type: "ArkSaveLogger.LogTypes", color: "ArkSaveLogger.LogColors" = None):
        if ArkSaveLogger._log_level_states is None:
            ArkSaveLogger.__init_log_levels()

        if (not ArkSaveLogger._log_level_states[log_type]) and not ArkSaveLogger._log_level_states["all"]:
            return
        
        if color is None:
            color = ArkSaveLogger.LogColors.WHITE

        message = f"{color}[{log_type}]{ArkSaveLogger.LogColors.RESET} {message}"

        print(message)

    @staticmethod
    def set_log_level(log_type: "ArkSaveLogger.LogTypes", state: bool, set_globally: bool = False):
        if ArkSaveLogger._log_level_states is None:
            ArkSaveLogger.__init_log_levels()
        ArkSaveLogger._log_level_states[log_type] = state

        if set_globally:
            global_config = read_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME)
            global_config[log_type] = state
            write_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME, global_config)

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
    def enable_hex_view(state: bool = True):
        ArkSaveLogger._file_viewer_enabled = state

    @staticmethod
    def reset_struct_path():
        ArkSaveLogger.current_struct_path = []

    @staticmethod
    def set_file(reader: "ArkBinaryParser", name: str):
        if ArkSaveLogger._temp_file_path != "" and ArkSaveLogger._file_viewer_enabled:
            ArkSaveLogger._byte_buffer = reader
            ArkSaveLogger._file = ArkSaveLogger._temp_file_path / name
            with open(ArkSaveLogger._file, 'wb') as f:
                f.write(reader.byte_buffer)

    @staticmethod
    def open_hex_view(wait: bool = False):
        if ArkSaveLogger._file_viewer_enabled and ArkSaveLogger._byte_buffer is not None:
            parser = Path(__file__).resolve().parent.parent.parent / 'binary-reader' / 'binary_visualizer.py'
            logging.info("[File viewer] Opening hex view")
            subprocess.Popen(['python', parser, '-f', ArkSaveLogger._file, '-i', str(ArkSaveLogger._byte_buffer.get_position())])
            if wait:
                input("Press Enter to continue...")