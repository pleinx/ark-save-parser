
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.struct.actor_transform import ActorTransform
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser

from .stats import DinoStats

class Dino:
    binary: ArkBinaryParser
    object: ArkGameObject

    id1: int
    id2: int

    is_female: bool
    is_cryopodded: bool

    gene_traits: list
    stats: DinoStats
    location: ActorTransform

    def _get_class_name(self):
        self.binary.set_position(0)
        class_name = self.binary.read_name()
        return class_name

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None, save: AsaSave = None):
        if binary is not None:
            self.is_cryopodded = False
            self.binary = binary
            bp = self._get_class_name()
            self.object = ArkGameObject(uuid=uuid, blueprint=bp, binary_reader=binary)

            self.is_female = self.object.get_property_value("bIsFemale", False)

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

    @staticmethod
    def from_object(obj: ArkGameObject, dino: "Dino" = None, is_cryopodded: bool = False):
        if dino is not None:
            d = dino
        else:
            d: Dino = Dino()

        d.is_cryopodded = is_cryopodded
        d.object = obj
        d.id1 = obj.get_property_value("DinoID1")
        d.id2 = obj.get_property_value("DinoID2")
        d.gene_traits = obj.get_array_property_value("GeneTraits")
        d.location = None
        if obj.get_property_value("SavedBaseWorldLocation") is not None:
            d.location = ActorTransform(vector=obj.get_property_value("SavedBaseWorldLocation"))

        return d


    
