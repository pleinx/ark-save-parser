
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.struct.actor_transform import ActorTransform
from arkparse.objects.saves.game_objects.abstract_game_object import AbstractGameObject
from arkparse.parsing import ArkBinaryParser

from .stats import DinoStats

class Dino:
    binary: ArkBinaryParser
    object: AbstractGameObject

    id1: int
    id2: int

    gene_traits: list
    stats: DinoStats
    location: ActorTransform

    def _get_class_name(self):
        self.binary.set_position(0)
        class_name = self.binary.read_name()
        return class_name

    def __init__(self, uuid: UUID, binary: ArkBinaryParser, save: AsaSave):
        self.binary = binary
        bp = self._get_class_name()
        self.object = AbstractGameObject(uuid=uuid, blueprint=bp, binary_reader=binary)

        self.id1 = self.object.get_property_value("DinoID1")
        self.id2 = self.object.get_property_value("DinoID2")

        self.gene_traits = self.object.get_array_property_value("GeneTraits")
        self.location = ActorTransform(vector=self.object.get_property_value("SavedBaseWorldLocation"))

        if self.object.get_property_value("MyCharacterStatusComponent") is not None:
            stat_uuid = self.object.get_property_value("MyCharacterStatusComponent").value
            bin = save.get_game_obj_binary(UUID(stat_uuid))
            parser = ArkBinaryParser(bin, save.save_context)
            self.stats = DinoStats(stat_uuid, parser)
        else:
            self.stats = DinoStats()


    
