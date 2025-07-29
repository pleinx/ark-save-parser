import pytest
from pathlib import Path

from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.logging import ArkSaveLogger

ArkSaveLogger.disable_all_logs()
# ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.WARNING, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.INFO, True)
ArkSaveLogger.allow_invalid_objects(False)

def file_directory(set: str) -> Path:
    """
    Returns the directory of the current file.
    """
    return Path(__file__).parent / "test_data" / set

def save_path(map: ArkMap, set: str = "set_1"):
    """
    Returns the path to the save file for the given map.
    """
    return file_directory(set) / f"{map.to_file_name()}_WP" / f"{map.to_file_name()}_WP.ark"

@pytest.fixture(scope="session")
def resource_path() -> Path:
    """
    Returns the path to the resource directory.
    """
    return Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def temp_file_folder() -> Path:
    """
    Returns the path to the temporary file folder.
    """
    path = Path(__file__).parent / "temp_files"

    # remove existing folder
    if path.exists():
        for item in path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                import shutil
                shutil.rmtree(item)
    
    # create folder
    path.mkdir(parents=True, exist_ok=True)
    return path

@pytest.fixture(scope="session")
def enabled_maps():
    """
    Returns a list of enabled ArkMaps.
    """
    return [
        # ArkMap.ABERRATION,
        # ArkMap.EXTINCTION,
        ArkMap.RAGNAROK,
        # ArkMap.SCORCHED_EARTH,
        # ArkMap.THE_CENTER,
        # ArkMap.THE_ISLAND,
        # ArkMap.ASTRAEOS
    ]

@pytest.fixture(scope="session")
def ragnarok_save():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.RAGNAROK))
    yield resource

@pytest.fixture(scope="session")
def rag_limited():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.RAGNAROK, "set_2"))
    yield resource

@pytest.fixture(scope="session")
def aberration_save():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.ABERRATION))
    yield resource

@pytest.fixture(scope="session")
def extinction_save():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.EXTINCTION))
    yield resource

@pytest.fixture(scope="session")
def astraeos_save():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.ASTRAEOS))
    yield resource

@pytest.fixture(scope="session")
def scorched_earth_save():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.SCORCHED_EARTH))
    yield resource

@pytest.fixture(scope="session")
def the_island_save():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.THE_ISLAND))
    yield resource

@pytest.fixture(scope="session")
def the_center_save():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.THE_CENTER))
    yield resource