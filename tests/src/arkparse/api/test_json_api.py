from pyparsing import Path
import pytest

from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.api.json_api import JsonApi

def test_export_ragnarok_objects(ragnarok_save: AsaSave, temp_file_folder: Path, enabled_maps: list):
    """
    Test to retrieve all objects from a Ragnarok save file.
    """
    if not ArkMap.RAGNAROK in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")
    JsonApi(ragnarok_save).export_all(export_folder_path=temp_file_folder / "json_exports_ragnarok")

def test_export_aberration_objects(aberration_save: AsaSave, temp_file_folder: Path, enabled_maps: list):
    """
    Test to retrieve all objects from an Aberration save file.
    """
    if not ArkMap.ABERRATION in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    JsonApi(aberration_save).export_all(export_folder_path=temp_file_folder / "json_exports_aberration")

def test_export_extinction_objects(extinction_save: AsaSave, temp_file_folder: Path, enabled_maps: list):
    """
    Test to retrieve all objects from an Extinction save file.
    """
    if not ArkMap.EXTINCTION in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    JsonApi(extinction_save).export_all(export_folder_path=temp_file_folder / "json_exports_extinction")

def test_export_astraeos_objects(astraeos_save: AsaSave, temp_file_folder: Path, enabled_maps: list):
    """
    Test to retrieve all objects from an Astraeos save file.
    """
    if not ArkMap.ASTRAEOS in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    JsonApi(astraeos_save).export_all(export_folder_path=temp_file_folder / "json_exports_astraeos")

def test_export_scorched_earth_objects(scorched_earth_save: AsaSave, temp_file_folder: Path, enabled_maps: list):
    """
    Test to retrieve all objects from a Scorched Earth save file.
    """
    if not ArkMap.SCORCHED_EARTH in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    JsonApi(scorched_earth_save).export_all(export_folder_path=temp_file_folder / "json_exports_scorched_earth")

def test_export_the_island_objects(the_island_save: AsaSave, temp_file_folder: Path, enabled_maps: list):
    """
    Test to retrieve all objects from a The Island save file.
    """
    if not ArkMap.THE_ISLAND in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")
    JsonApi(the_island_save).export_all(export_folder_path=temp_file_folder / "json_exports_the_island")

def test_export_the_center_objects(the_center_save: AsaSave, temp_file_folder: Path, enabled_maps: list):
    """
    Test to retrieve all objects from a The Center save file.
    """
    if not ArkMap.THE_CENTER in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    JsonApi(the_center_save).export_all(export_folder_path=temp_file_folder / "json_exports_the_center")