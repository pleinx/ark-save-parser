from typing import Dict
from uuid import UUID, uuid4
from pathlib import Path
import os

from arkparse.api.structure_api import StructureApi
from arkparse.parsing.struct.actor_transform import MapCoords
from arkparse.object_model.structures import Structure
from arkparse.object_model.bases.base import Base
from arkparse.enums import ArkMap
from arkparse.parsing.struct import ActorTransform
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model import ArkGameObject

class BaseApi(StructureApi):
    def __init__(self, save, map: ArkMap):
        super().__init__(save)
        self.map = map

    def __get_closest_to(self, structures: Dict[UUID, Structure], coords: MapCoords):
        closest = None
        closest_dist = None

        for key, structure in structures.items():
            s_coords = structure.location.as_map_coords(self.map)
            dist = s_coords.distance_to(coords)
            if closest is None or dist < closest_dist:
                closest = structure
                closest_dist = dist

        return closest


    def get_base_at(self, coords: MapCoords) -> Base:
        structures = self.get_at_location(self.map, coords)
        if structures is None:
            return None
        
        all_structures = {}
        for key, structure in structures.items():
            all_structures[key] = structure
            connected = self.get_connected_structures(structures)
            for key, conn_structure in connected.items():
                if key not in all_structures:
                    all_structures[key] = conn_structure

        keystone = self.__get_closest_to(all_structures, coords)

        # todo: remove all structures not owned by the same owner as keystone

        return Base(keystone.object.uuid, all_structures)
    
    def __get_all_files_from_dir_recursive(self, dir_path: Path) -> Dict[str, bytes]:
        out = {}
        def read_bytes_from_file(file_path: Path) -> bytes:
            with open(file_path, "rb") as f:
                return f.read()

        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / Path(file)
                out[str(file_path)] = read_bytes_from_file(file_path)

        return out
    
    def import_base(self, path: Path):
        uuid_translation_map = {}
        # interconnection_properties = [
        #     "PlacedOnFloorStructure",
        #     "MyInventoryComponent",
        #     "WirelessSources",
        #     "WirelessConsumers",
        #     "InventoryItems",
        #     "OwnerInventory",
        #     "StructuresPlacedOnFloor",
        #     "LinkedStructures"
        # ]

        actor_transforms: Dict[UUID, ActorTransform] = {}
        structures: Dict[UUID, Structure] = {}

        files: Dict[str, bytes] = self.__get_all_files_from_dir_recursive(path)

        base_file = None
        for file_path, file_bytes in files.items():
            if file_path.split("\\")[-1] == "base.json":
                base_file = file_path
        files.pop(base_file)

        # Assign new uuids to all actor transforms and add them to the database
        for file_path, _ in files.items():
            file = file_path.split("\\")[-1]
            uuid = file.split("_")[0]
            try:
                t = file.split("_")[1]
            except:
                print(file)
                raise
            # t = file.split("_")[1]

            if t == "loc":
                new_uuid = uuid4()
                uuid_translation_map[uuid] = new_uuid
                actor_transforms[new_uuid] = ActorTransform(from_json=Path(file_path))
                self.save.add_new_actor_transform_to_db(new_uuid, actor_transforms[new_uuid])

        # Update actor transforms in save context
        self.save.read_actor_locations()

        # Parse structures
        for file_path, file_bytes in files.items():
            file = file_path.split("\\")[-1]
            uuid = file.split("_")[0]
            t = file.split("_")[1]

            if t == "obj":
                if uuid in uuid_translation_map:
                    new_uuid = uuid_translation_map[UUID(uuid)]
                else:
                    new_uuid = uuid4()
                    uuid_translation_map[uuid] = new_uuid
                    parser = ArkBinaryParser(file_bytes, self.save.save_context)
                    obj = ArkGameObject(uuid=new_uuid, binary_reader=parser)
                    structure = self._parse_single_structure(obj)
                    structure.reidentify(new_uuid=new_uuid)
                    structures[new_uuid] = structure

        # Update all interconnection properties
        for key, structure in structures.items():
            for uuid in uuid_translation_map:
                structure.replace_uuid(uuid_translation_map[uuid], uuid)

                # validate that parsing still works for all objects
                parser = ArkBinaryParser(structure.binary.byte_buffer, self.save.save_context)
                obj = ArkGameObject(uuid=key, binary_reader=parser)

                # insert object into save
                self.save.add_obj_to_db(key, structure.binary.byte_buffer)

        return structures

                

        

    

        
