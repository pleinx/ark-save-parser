import pytest
from pathlib import Path
from arkparse.api.dino_api import DinoApi
from arkparse import AsaSave
from arkparse.object_model.dinos import Dino, TamedDino

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

def test_get_all_dinos(dino_api: DinoApi):
    """
    Test to retrieve all tamed dinos from the Ragnarok save.
    """
    dinos = dino_api.get_all()
    assert isinstance(dinos, dict), "Expected a dictionary of dinos"
    print(f"Total dinos found: {len(dinos)}")
    assert len(dinos) > 0, "Expected to find at least one dino"