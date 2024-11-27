from typing import Dict, Union, List
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration, ArkBinaryParser
from arkparse.logging import ArkSaveLogger

from arkparse.objects.saves.game_objects import ArkGameObject, ArkGameObject
from arkparse.objects.saves.game_objects.misc.object_owner import ObjectOwner
from arkparse.objects.saves.game_objects.structures import SimpleStructure, StructureWithInventory
from arkparse.struct.actor_transform import MapCoords
from arkparse.enums.ark_map import ArkMap

class StructureApi:
    def __init__(self, save: AsaSave):
        self.save = save

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        if config is None:
            reader_config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and "/Structures" in name and not "PrimalItemStructure_" in name
            )
        else:
            reader_config = config

        objects = self.save.get_game_objects(reader_config)

        return objects
    
    def __parse_single_structure(self, obj: ArkGameObject) -> Union[SimpleStructure, StructureWithInventory]:
        if obj.get_property_value("MyInventoryComponent") is not None:
            parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
            structure = StructureWithInventory(obj.uuid, parser, self.save)
        else:
            parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
            structure = SimpleStructure(obj.uuid, parser)
        
        for key, loc in self.save.save_context.actor_transforms.items():
            if key == obj.uuid:
                structure.set_actor_transform(loc)

        return structure

    def get_all(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, Union[SimpleStructure, StructureWithInventory]]:
        
        objects = self.get_all_objects(config)

        structures = {}

        for key, obj in objects.items():
            obj : ArkGameObject = obj
            if obj is None:
                print(f"Object is None for {key}")
                continue
            
            structure = self.__parse_single_structure(obj)

            structures[obj.uuid] = structure

        return structures
    
    def get_by_id(self, id: UUID) -> Union[SimpleStructure, StructureWithInventory]:
        obj = self.save.get_game_object_by_id(id)
        return self.__parse_single_structure(obj)
    
    def get_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3) -> Dict[UUID, Union[SimpleStructure, StructureWithInventory]]:
        structures = self.get_all()
        result = {}

        for key, obj in structures.items():
            obj: SimpleStructure = obj
            if obj.location is None:
                continue

            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result[key] = obj

        return result
    
    def get_owned_by(self, owner: ObjectOwner) -> Dict[UUID, Union[SimpleStructure, StructureWithInventory]]:
        result = {}
        
        if owner is None:
            return result

        structures = self.get_all()
        
        for key, obj in structures.items():
            if obj.is_owned_by(owner):
                result[key] = obj

        return result
    
    def get_by_class(self, blueprints: List[str]) -> Dict[UUID, Union[SimpleStructure, StructureWithInventory]]:
        result = {}

        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name in blueprints
        )

        structures = self.get_all(config)

        for key, obj in structures.items():
            result[key] = obj

        return result
    
    def filter_by_owner(self, owner: ObjectOwner, structures: Dict[UUID, Union[SimpleStructure, StructureWithInventory]]) -> Dict[UUID, Union[SimpleStructure, StructureWithInventory]]:
        result = {}

        for key, obj in structures.items():
            if obj.is_owned_by(owner):
                result[key] = obj

        return result
    
    def filter_by_location(self, map: ArkMap, coords: MapCoords, radius: float, structures: Dict[UUID, Union[SimpleStructure, StructureWithInventory]]) -> Dict[UUID, Union[SimpleStructure, StructureWithInventory]]:
        result = {}

        for key, obj in structures.items():
            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result[key] = obj

        return result
    
    def get_connected_structures(self, structures: Dict[UUID, Union[SimpleStructure, StructureWithInventory]]) -> Dict[UUID, Union[SimpleStructure, StructureWithInventory]]:
        result = structures.copy()
        new_found = True

        while new_found:
            new_found = False
            new_result = result.copy()
            for key, s in result.items():
                for uuid in s.linked_structure_uuids:
                    if uuid not in new_result.keys():
                        new_found = True
                        obj = self.get_by_id(uuid)
                        new_result[uuid] = obj
            result = new_result

        return result
     
    def transfer_ownership(self, owner: ObjectOwner, structures: Dict[UUID, Union[SimpleStructure, StructureWithInventory]]):
        for key, obj in structures.items():
            for uuid in obj.linked_structure_uuids:
                if uuid not in structures.keys():
                    raise ValueError(f"Linked structure {uuid} is not in the structures list, please change owner of all linked structures")

            obj.owner.replace_self_with(owner)
            obj.binary = obj.owner.set_in_binary(obj.binary)
            self.save.modify_obj_in_db(obj.object.uuid, obj.binary.byte_buffer)