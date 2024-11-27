import os
from pathlib import Path

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
    temp_files_dir.mkdir(parents=True, exist_ok=True)
    return temp_files_dir

TEMP_FILES_DIR = __create_temp_files_folder()