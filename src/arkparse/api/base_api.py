from typing import Dict
from uuid import UUID
from pathlib import Path

from arkparse.api.structure_api import StructureApi
from arkparse.parsing.struct.actor_transform import MapCoords
from arkparse.object_model.structures import Structure
from arkparse.object_model.bases.base import Base
from arkparse.enums import ArkMap

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
    
    def import_base(self, path: Path):
        uuid_translation_map = {}
        interconnection_properties = [
            "PlacedOnFloorStructure",
            "MyInventoryComponent",
            "WirelessSources",
            "WirelessConsumers",
            "InventoryItems",
            "OwnerInventory",
            "StructuresPlacedOnFloor",
            "LinkedStructures"
            
        ]