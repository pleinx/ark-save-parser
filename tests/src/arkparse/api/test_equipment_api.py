import pytest
from pathlib import Path
from arkparse.api import EquipmentApi
from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.logging import ArkSaveLogger

def equipment_per_map():
    """ Fixture to provide the expected number of equipment for each map. """
    return {
        ArkMap.RAGNAROK: {
            "armor": 1906,
            "weapons": 1517,
            "saddles": 2161,
            "shields": 87
        },
        ArkMap.ABERRATION: {
            "armor": 1024,
            "weapons": 394,
            "saddles": 481,
            "shields": 27
        },
        ArkMap.EXTINCTION: {
            "armor": 4279,
            "weapons": 2649,
            "saddles": 3110,
            "shields": 80
        },
        ArkMap.ASTRAEOS: {
            "armor": 6120,
            "weapons": 3757,
            "saddles": 8100,
            "shields": 205
        },
        ArkMap.SCORCHED_EARTH: {
            "armor": 1594,
            "weapons": 818,
            "saddles": 1565,
            "shields": 33
        },
        ArkMap.THE_ISLAND: {
            "armor": 6143,
            "weapons": 3857,
            "saddles": 6555,
            "shields": 216
        },
        ArkMap.THE_CENTER: {
            "armor": 6480,
            "weapons": 3818,
            "saddles": 7418,
            "shields": 208
        }
    }

@pytest.fixture(scope="module")
def eq_api(ragnarok_save):
    """
    Fixture to provide a EquipmentApi instance for the Ragnarok save.
    """
    resource = EquipmentApi(ragnarok_save)
    yield resource

def get_for_map(map_name: ArkMap, api: EquipmentApi):
    print(f"Testing equipment for map: {map_name}")

    armor = api.get_armor()
    print(f"Total Armor Items: {len(armor)}")
    assert len(armor) == equipment_per_map()[map_name]["armor"], "Unexpected number of armor items found"

    weapons = api.get_weapons()
    print(f"Total Weapon Items: {len(weapons)}")
    assert len(weapons) == equipment_per_map()[map_name]["weapons"], "Unexpected number of weapon items found."

    saddles = api.get_saddles()
    print(f"Total Saddle Items: {len(saddles)}")
    assert len(saddles) == equipment_per_map()[map_name]["saddles"], "Unexpected number of saddle items found."

    shields = api.get_shields()
    print(f"Total Shield Items: {len(shields)}")
    assert len(shields) == equipment_per_map()[map_name]["shields"], "Unexpected number of shield items found."

def test_parse_ragnarok(eq_api: EquipmentApi, enabled_maps: list):
    """
    Test to parse the Ragnarok save file and check the number of dinos.
    """
    if not ArkMap.RAGNAROK in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")

    get_for_map(ArkMap.RAGNAROK, eq_api)

def test_parse_aberration(aberration_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Aberration save file and check the number of dinos.
    """
    if not ArkMap.ABERRATION in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    eq_api = EquipmentApi(aberration_save)
    
    get_for_map(ArkMap.ABERRATION, eq_api)

def test_parse_extinction(extinction_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Extinction save file and check the number of dinos.
    """
    if not ArkMap.EXTINCTION in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    eq_api = EquipmentApi(extinction_save)

    get_for_map(ArkMap.EXTINCTION, eq_api)

def test_parse_astraeos(astraeos_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Astraeos save file and check the number of dinos.
    """
    if not ArkMap.ASTRAEOS in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    eq_api = EquipmentApi(astraeos_save)

    get_for_map(ArkMap.ASTRAEOS, eq_api)

def test_parse_scorched_earth(scorched_earth_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Scorched Earth save file and check the number of dinos.
    """
    if not ArkMap.SCORCHED_EARTH in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    eq_api = EquipmentApi(scorched_earth_save)

    get_for_map(ArkMap.SCORCHED_EARTH, eq_api)

def test_parse_the_island(the_island_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Island save file and check the number of dinos.
    """
    if not ArkMap.THE_ISLAND in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")
    eq_api = EquipmentApi(the_island_save)

    get_for_map(ArkMap.THE_ISLAND, eq_api)

def test_parse_the_center(the_center_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Center save file and check the number of dinos.
    """
    if not ArkMap.THE_CENTER in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    eq_api = EquipmentApi(the_center_save)
    get_for_map(ArkMap.THE_CENTER, eq_api)