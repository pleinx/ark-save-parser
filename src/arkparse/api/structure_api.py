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


    def get_all(self, config: GameObjectReaderConfiguration = None) -> Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]:
        
        objects = self.get_all_objects(config)

        structures = {
            "structures": {},
            "structures_with_inventory": {}
        }

        for key, obj in objects.items():
            obj : ArkGameObject = obj
            if obj is None:
                print(f"Object is None for {key}")
                continue
            
            structure = None
            type_ = ""

            if obj.get_property_value("MyInventoryComponent") is not None:
                parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid))
                parser.save_context = self.save.save_context
                structure = StructureWithInventory(obj.uuid, parser, self.save)
                type_ = "structures_with_inventory"
            else:
                parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid))
                parser.save_context = self.save.save_context
                structure = SimpleStructure(obj.uuid, parser)
                type_ = "structures"
            
            for key, loc in self.save.save_context.actor_transforms.items():
                if key == obj.uuid:
                    structure.set_actor_transform(loc)

            structures[type_][obj.uuid] = structure

        return structures
    
    def get_by_id(self, id: UUID) -> Union[SimpleStructure, StructureWithInventory]:
        obj = self.save.get_game_object_by_id(id)

        if obj.get_property_value("MyInventoryComponent") is not None:
            parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid))
            parser.save_context = self.save.save_context
            structure = StructureWithInventory(obj.uuid, parser, self.save)
        else:
            parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid))
            parser.save_context = self.save.save_context
            structure = SimpleStructure(obj.uuid, parser)
        
        for key, loc in self.save.save_context.actor_transforms.items():
            if key == obj.uuid:
                structure.set_actor_transform(loc)

        return structure
    
    def get_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3) -> Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]:
        structures = self.get_all()
        result = {
            "structures": {},
            "structures_with_inventory": {}
        }

        for key, obj in structures["structures"].items():
            if obj.location is None:
                print(f"Location is None for {obj.object.uuid}")
                continue

            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result["structures"][key] = obj

        for key, obj in structures["structures_with_inventory"].items():
            if obj.location is None:
                print(f"Location is None for {obj.object.uuid}")
                continue

            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result["structures_with_inventory"][key] = obj

        return result
    
    def get_owned_by(self, owner: ObjectOwner) -> Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]:
        result = {
            "structures": {},
            "structures_with_inventory": {}
        }
        
        if owner is None:
            return result

        structures = self.get_all()
        
        for key, obj in structures["structures"].items():
            if obj.is_owned_by(owner):
                result["structures"][key] = obj

        for key, obj in structures["structures_with_inventory"].items():
            if obj.is_owned_by(owner):
                result["structures_with_inventory"][key] = obj

        return result
    
    def get_by_class(self, blueprints: List[str]) -> Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]:
        result = {
            "structures": {},
            "structures_with_inventory": {}
        }

        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name in blueprints
        )

        structures = self.get_all(config)

        for key, obj in structures["structures"].items():
            result["structures"][key] = obj

        for key, obj in structures["structures_with_inventory"].items():
            result["structures_with_inventory"][key] = obj

        return result
    
    def filter_by_owner(self, owner: ObjectOwner, structures: Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]) -> Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]:
        result = {
            "structures": {},
            "structures_with_inventory": {}
        }

        for key, obj in structures["structures"].items():

            if obj.is_owned_by(owner):
                result["structures"][key] = obj

        for key, obj in structures["structures_with_inventory"].items():
            if obj.is_owned_by(owner):
                result["structures_with_inventory"][key] = obj

        return result
    
    def filter_by_location(self, map: ArkMap, coords: MapCoords, radius: float, structures: Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]) -> Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]:
        result = {
            "structures": {},
            "structures_with_inventory": {}
        }

        for key, obj in structures["structures"].items():
            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result["structures"][key] = obj

        for key, obj in structures["structures_with_inventory"].items():
            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result["structures_with_inventory"][key] = obj

        return result
     
    def transfer_ownership(self, owner: ObjectOwner, structures: Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]):
        for key, obj in structures["structures"].items():
            obj.set_owner(owner)

        for key, obj in structures["structures_with_inventory"].items():
            obj.set_owner(owner)

    def get_response_total_count(self, response: Dict[str, Dict[UUID, Union[SimpleStructure, StructureWithInventory]]]) -> int:
        return len(response["structures"]) + len(response["structures_with_inventory"])