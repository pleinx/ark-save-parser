import pytest
from pathlib import Path
from arkparse.api import BaseApi
from arkparse.enums import ArkMap
from arkparse import AsaSave
from arkparse.player.ark_player import ArkPlayer
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.parsing.struct import ActorTransform, ArkVector

def count_files_in_folder(folder: Path) -> int:
    """
    Counts the number of files in a given folder.
    """
    if not folder.exists():
        return 0
    return sum(1 for _ in folder.iterdir() if _.is_file())

def get_base_api(rag_limited: AsaSave, temp_file_folder: Path) -> BaseApi:
    rag_limited.store_db(temp_file_folder / "copy.db")
    assert (temp_file_folder / "copy.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'copy.db'}")
    save = AsaSave(path=temp_file_folder / "copy.db")
    assert save is not None, "AsaSave should be initialized"
    return BaseApi(save, ArkMap.RAGNAROK)

def test_base_api_initialization(rag_limited: AsaSave, resource_path: Path, temp_file_folder: Path):
    """
    Test the initialization of the BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    assert base_api is not None, "BaseApi should be initialized"
    assert isinstance(base_api, BaseApi), f"Expected BaseApi, got {type(base_api)}"
    assert base_api.save is not None, "BaseApi save should not be None"

def test_base_import(resource_path, temp_file_folder, rag_limited: AsaSave):
    """
    Test the import functionality of BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"
    print(f"Imported {count_files_in_folder(base_path)} files from base, base has {len(base.structures)} structures")

    base_api.save.store_db(temp_file_folder / "test_base_import.db")
    assert (temp_file_folder / "test_base_import.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_base_import.db'}")

    reimport_save = AsaSave(path = temp_file_folder / "test_base_import.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"
    print(f"Re-imported base has {len(reimport_base.structures)} structures, nr of files: {count_files_in_folder(temp_file_folder / 'test_base_import')}")

    reimport_base.store_binary(temp_file_folder / "test_export")
    print(f"Exported {count_files_in_folder(temp_file_folder / 'test_export')} files to {temp_file_folder / 'test_export'}")

    assert count_files_in_folder(temp_file_folder / "test_export") > 0, "Exported files should exist"
    assert count_files_in_folder(temp_file_folder / "test_export") == count_files_in_folder(base_path), "Exported files count should match the original base files"

def test_base_import_at_location(resource_path, temp_file_folder, rag_limited: AsaSave):
    """
    Test the import functionality of BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    new_location = ActorTransform(vector=ArkVector(x=118368.11, y=172509.7, z=-10290))
    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path, new_location)
    assert base is not None, "Imported base should not be None"
    print(f"Imported {count_files_in_folder(base_path)} files from base, base has {len(base.structures)} structures")

    base_api.save.store_db(temp_file_folder / "test_base_import_at_location.db")
    assert (temp_file_folder / "test_base_import_at_location.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_base_import_at_location.db'}")

    reimport_save = AsaSave(path = temp_file_folder / "test_base_import_at_location.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(new_location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"
    print(f"Re-imported base has {len(reimport_base.structures)} structures, nr of files: {count_files_in_folder(temp_file_folder / 'test_base_import_at_location')}")

    reimport_base.store_binary(temp_file_folder / "test_export_at_location")
    print(f"Exported {count_files_in_folder(temp_file_folder / 'test_export_at_location')} files to {temp_file_folder / 'test_export_at_location'}")

    assert count_files_in_folder(temp_file_folder / "test_export_at_location") > 0, "Exported files should exist"
    assert count_files_in_folder(temp_file_folder / "test_export_at_location") == count_files_in_folder(base_path), "Exported files count should match the original base files"

def test_base_replace_owner(resource_path, temp_file_folder, rag_limited: AsaSave):
    """
    Test the replace owner functionality of BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"
    print(f"Imported {count_files_in_folder(base_path)} files from base, base has {len(base.structures)} structures")
    
    original_owner = base.owner
    o: ObjectOwner = ObjectOwner()
    o.set_tribe(171717, "Imaginarium")
    o.set_player(777, "The imagined")
    print(f"Replacing owner {original_owner} with {o}")

    base.set_owner(o, base_api.save)

    new_base_api = BaseApi(base_api.save, ArkMap.RAGNAROK)

    b = base_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    print(b.owner)

    base_api.save.store_db(temp_file_folder / "test_base_replace_owner.db")
    assert (temp_file_folder / "test_base_replace_owner.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_base_replace_owner.db'}")

    reimport_save = AsaSave(path=temp_file_folder / "test_base_replace_owner.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"
    print(f"Re-imported base has {len(reimport_base.structures)} structures, owner: {reimport_base.owner}")
    assert reimport_base.owner == o, (f"Expected owner {o}, got {reimport_base.owner}")
    print(f"Re-imported base owner: {reimport_base.owner}")

    reimport_base.store_binary(temp_file_folder / "test_export_replace_owner")
    print(f"Exported {count_files_in_folder(temp_file_folder / 'test_export_replace_owner')} files to {temp_file_folder / 'test_export_replace_owner'}")
    
    nr_of_structures_old = len(base.structures)
    nr_of_structures_new = len(reimport_base.structures)
    files_old = count_files_in_folder(resource_path / "bases" / "mixed_6")
    files_new = count_files_in_folder(temp_file_folder / "test_export_replace_owner")

    assert files_new == files_old, (
        f"Expected {files_old} files, got {files_new}"
    )

    assert nr_of_structures_new == nr_of_structures_old, (
        f"Expected {nr_of_structures_old} structures, got {nr_of_structures_new}"
    )

