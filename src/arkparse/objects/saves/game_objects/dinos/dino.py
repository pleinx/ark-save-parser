
from uuid import UUID

from arkparse.objects.saves.game_objects.misc.__parsed_object_base import ParsedObjectBase
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.struct.actor_transform import ActorTransform
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser

from .stats import DinoStats

class Dino(ParsedObjectBase):
    id1: int = 0
    id2: int = 0

    is_female: bool = False
    is_cryopodded: bool = False

    gene_traits: list = []
    stats: DinoStats = DinoStats()
    location: ActorTransform = ActorTransform()

    #saddle: Saddle

    def __init_props__(self, obj: ArkGameObject = None):
        if obj is not None:
            super().__init_props__(obj)

        self.is_female = self.object.get_property_value("bIsFemale", False)
        self.id1 = self.object.get_property_value("DinoID1")
        self.id2 = self.object.get_property_value("DinoID2")
        self.gene_traits = self.object.get_array_property_value("GeneTraits")
        self.location = ActorTransform(vector=self.object.get_property_value("SavedBaseWorldLocation"))
    
    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None, save: AsaSave = None):
        if binary is not None:
            super().__init__(uuid, binary)
            self.__init_props__()

            if save is not None and self.object.get_property_value("MyCharacterStatusComponent") is not None:
                stat_uuid = self.object.get_property_value("MyCharacterStatusComponent").value
                bin = save.get_game_obj_binary(UUID(stat_uuid))
                parser = ArkBinaryParser(bin, save.save_context)
                self.stats = DinoStats(stat_uuid, parser)

    def __str__(self) -> str:
        return "Dino(type={}, lv={})".format(self.get_short_name(), self.stats.current_level)

    @staticmethod
    def from_object(dino_obj: ArkGameObject, status_obj: ArkGameObject, dino: "Dino" = None):
        if dino is not None:
            d = dino
        else:
            d: Dino = Dino()
            d.__init_props__(dino_obj)

        d.stats = DinoStats.from_object(status_obj)

        return d    
    