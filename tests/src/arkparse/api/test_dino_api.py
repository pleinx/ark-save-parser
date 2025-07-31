import pytest
from pathlib import Path
from arkparse.api.dino_api import DinoApi
from arkparse import AsaSave
from arkparse.object_model.dinos import TamedDino
from arkparse.enums import ArkMap

@pytest.fixture(scope="module")
def dino_api(ragnarok_save):
    """
    Fixture to provide a DinoApi instance for the Ragnarok save.
    """
    return DinoApi(ragnarok_save)

@pytest.fixture(scope="module")
def dino_mod_api(rag_limited: AsaSave, temp_file_folder: Path):
    """
    Helper function to get the DinoApi instance for the rag_limited save.
    """
    rag_limited.store_db(temp_file_folder / "copy.db")
    assert (temp_file_folder / "copy.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'copy.db'}")
    save = AsaSave(path=temp_file_folder / "copy.db")
    assert save is not None, "AsaSave should be initialized"
    return DinoApi(save)

def test_parse_ragnarok(ragnarok_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Ragnarok save file and check the number of dinos.
    """
    if not ArkMap.RAGNAROK in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")
    dinos = DinoApi(ragnarok_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Ragnarok: {len(dinos)}")

def test_parse_aberration(aberration_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Aberration save file and check the number of dinos.
    """
    if not ArkMap.ABERRATION in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    dinos = DinoApi(aberration_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Aberration: {len(dinos)}")

def test_parse_extinction(extinction_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Extinction save file and check the number of dinos.
    """
    if not ArkMap.EXTINCTION in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    dinos = DinoApi(extinction_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Extinction: {len(dinos)}")

def test_parse_astraeos(astraeos_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Astraeos save file and check the number of dinos.
    """
    if not ArkMap.ASTRAEOS in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    dinos = DinoApi(astraeos_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Astraeos: {len(dinos)}")

def test_parse_scorched_earth(scorched_earth_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Scorched Earth save file and check the number of dinos.
    """
    if not ArkMap.SCORCHED_EARTH in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    dinos = DinoApi(scorched_earth_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Scorched Earth: {len(dinos)}")

def test_parse_the_island(the_island_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Island save file and check the number of dinos.
    """
    if not ArkMap.THE_ISLAND in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")
    dinos = DinoApi(the_island_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in The Island: {len(dinos)}")

def test_parse_the_center(the_center_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Center save file and check the number of dinos.
    """
    if not ArkMap.THE_CENTER in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    dinos = DinoApi(the_center_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in The Center: {len(dinos)}")

def test_get_all_dinos(dino_api: DinoApi):
    """
    Test to retrieve all tamed dinos from the Ragnarok save.
    """
    dinos = dino_api.get_all()
    assert isinstance(dinos, dict), "Expected a dictionary of dinos"
    print(f"Total dinos found: {len(dinos)}")
    assert len(dinos) > 0, "Expected to find at least one dino"