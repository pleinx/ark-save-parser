from typing import Dict, List
from uuid import UUID

from arkparse.objects.saves.game_objects.resources.resource import Resource
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration

class ResourceApi:
    def __init__(self, save: AsaSave):
        self.save = save
        self.all_objects = None

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        if config is None:
            if self.all_objects is not None:
                return self.all_objects

            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and "Resources/PrimalItemResource" in name
            )

        objects = self.save.get_game_objects(config)
        self.all_objects = objects

        return objects
    
    def get_all(self, config = None) -> Dict[UUID, Resource]:
        objects = self.get_all_objects(config)

        resources = {}

        for key, obj in objects.items():
            is_bp = obj.get_property_value("bIsInitialItem")
            is_engram = obj.get_property_value("bIsEngram")

            if is_bp or is_engram:
                continue

            parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
            resources[key] = Resource(obj.uuid, parser)

        return resources
    
    def get_by_class(self, classes: List[str]) -> Dict[UUID, Resource]:
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and name in classes
        )

        objects = self.get_all_objects(config)

        resources = {}

        for key, obj in objects.items():
            parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
            resources[key] = Resource(obj.uuid, parser)

        return resources
    
    def get_count(self, resources: Dict[UUID, Resource]) -> int:
        count = 0

        for res in resources.values():
            count += res.quantity

        return count

    