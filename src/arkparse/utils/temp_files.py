import os
from pathlib import Path
import errno

__TEMP_FILE_DIR_CLEARED = False

def __create_temp_files_folder():
    """
    Creates a folder named `asp/temp_files` under the appropriate directory
    depending on the operating system:
    - On Windows: uses LOCALAPPDATA.
    - On Linux/macOS: uses ~/.cache.
    
    Returns:
        Path: The Path object of the created directory.
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.getenv('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    else:  # Linux/macOS
        base_dir = Path(os.getenv('XDG_CACHE_HOME', Path.home() / '.cache'))
    
    temp_files_dir = base_dir / 'asp' / 'temp_files'

    global __TEMP_FILE_DIR_CLEARED
    if not __TEMP_FILE_DIR_CLEARED:
        # Clear the temp files directory if it exists
        if temp_files_dir.exists():
            for item in temp_files_dir.iterdir():
                try:
                    if item.is_file() or item.is_symlink():
                        item.unlink()
                    elif item.is_dir():
                        for sub_item in item.iterdir():
                            try:
                                sub_item.unlink()
                            except OSError as e:
                                if e.errno != errno.EACCES:
                                    raise
                                # Ignore locked files
                        item.rmdir()
                except OSError as e:
                    if e.errno != errno.EACCES:
                        raise
                    # Ignore locked files
        __TEMP_FILE_DIR_CLEARED = True
        
    temp_files_dir.mkdir(parents=True, exist_ok=True)
    return temp_files_dir

TEMP_FILES_DIR = __create_temp_files_folder()