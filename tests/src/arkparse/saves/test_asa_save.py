import pytest
import time
from pathlib import Path
from uuid import UUID, uuid4

from arkparse import AsaSave
from arkparse.parsing.struct import ActorTransform, ArkVector
from arkparse.logging import ArkSaveLogger

def test_nr_of_objects(rag_limited: AsaSave):
    objects = rag_limited.get_game_objects()
    print(f"Number of objects in save: {len(objects)}")
    assert len(objects) > 0, "AsaSave should have objects"

def test_get_nr_of_classes(rag_limited: AsaSave):
    classes = rag_limited.get_all_present_classes()
    print(f"Number of classes in save: {len(classes)}")
    assert len(classes) > 0, "AsaSave should have classes"

def test_add_actor_transform(rag_limited: AsaSave, temp_file_folder: Path):
    new_location = ActorTransform(vector=ArkVector(x=118368.11, y=172509.7, z=-10290))
    new_uuid: UUID = uuid4()
    max_delta = 100
    rag_limited.add_actor_transform(new_uuid, new_location.to_bytes())
    rag_limited.read_actor_locations()
    at = rag_limited.save_context.get_actor_transform(new_uuid)

    print(f"Added actor transform at location: {new_location}")
    print(f"Actor transform UUID: {new_uuid}")
    print(f"Actor transform distance to new location: {at.get_distance_to(new_location)}")

    assert at is not None, "Actor transform should be added to save"
    assert at.get_distance_to(new_location) < max_delta, (
        f"Actor transform should be close to the new location, got {at.get_distance_to(new_location)}"
    )

    # store and reparse the save
    rag_limited.store_db(temp_file_folder / "test_add_actor_transform.db")
    reparse_save = AsaSave(path=temp_file_folder / "test_add_actor_transform.db")
    at = reparse_save.save_context.get_actor_transform(new_uuid)
    assert at is not None, "Actor transform should still be present after reparsing the save"
    print(f"Actor transform distance after reparsing: {at.get_distance_to(new_location)}")
    assert at.get_distance_to(new_location) < max_delta, (
        f"Actor transform should still be close to the new location after reparsing, got {at.get_distance_to(new_location)}"
    )

def test_modify_actor_transform(rag_limited: AsaSave, temp_file_folder: Path):
    new_location = ActorTransform(vector=ArkVector(x=118368.11, y=172509.7, z=-10290))
    new_uuid: UUID = uuid4()
    rag_limited.add_actor_transform(new_uuid, new_location.to_bytes())
    rag_limited.read_actor_locations()
    
    # Modify the actor transform
    modified_location = ActorTransform(vector=ArkVector(x=7777.0, y=7777.0, z=-7777))
    rag_limited.modify_actor_transform(new_uuid, modified_location.to_bytes())
    
    rag_limited.store_db(temp_file_folder / "test_modify_actor_transform.db")
    reparse_save = AsaSave(path=temp_file_folder / "test_modify_actor_transform.db")
    
    at = reparse_save.save_context.get_actor_transform(new_uuid)
    assert at is not None, "Actor transform should still be present after modification"
    print(f"Modified actor transform distance: {at.get_distance_to(modified_location)}")
    assert at.get_distance_to(modified_location) < 100, (
        f"Actor transform should be close to the modified location, got {at.get_distance_to(modified_location)}"
    )