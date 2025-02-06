
from uuid import UUID
from typing import List

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkDinoTrait

from .stats import DinoStats

class Dino(ParsedObjectBase):
    id1: int = 0
    id2: int = 0

    is_female: bool = False
    is_cryopodded: bool = False

    gene_traits: List[str] = []
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
                self.stats = DinoStats(UUID(stat_uuid), parser)

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

    def __get_gene_trait_bytes(self, trait: ArkDinoTrait, level: int, save: AsaSave) -> bytes:
        trait = f"{trait.value}[{level}]"
        trait_id = save.save_context.get_name_id(trait)

        gene_trait_id = save.save_context.get_name_id("GeneTraits")

        if gene_trait_id is None:
            save.add_name_to_name_table("GeneTraits")

        if trait_id is None:
            save.add_name_to_name_table(trait)
            trait_id = save.save_context.get_name_id(trait)
        
        return trait_id.to_bytes(4, byteorder="little") + b'\x00\x00\x00\x00'  
    
    def clear_gene_traits(self, save: AsaSave):
        gt = self.object.get_property_value("GeneTraits")
        self.gene_traits = []

        if gt is None:
            return

        self.binary.set_property_position("GeneTraits")
        self.binary.replace_array("GeneTraits", "NameProperty", None)
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)

    def remove_gene_trait(self, trait: ArkDinoTrait, save: AsaSave):
        self.gene_traits = [t for t in self.gene_traits if not t.startswith(trait.value)]

        gt = self.object.get_property_value("GeneTraits")

        if gt is None:
            return
        
        new_genes = [self.__get_gene_trait_bytes(ArkDinoTrait.from_string(t), int(t.split("[")[1][:-1]), save) for t in self.gene_traits]
        self.binary.set_property_position("GeneTraits")
        self.binary.replace_array("GeneTraits", "NameProperty", new_genes if len(new_genes) > 0 else None)
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)


    def add_gene_trait(self, trait: ArkDinoTrait, level: int, save: AsaSave):
        self.gene_traits.append(f"{trait.value}[{level}]")
        gt = self.object.get_property_value("GeneTraits")

        if gt is None:
            self.binary.set_property_position("SavedBaseWorldLocation")
            self.binary.insert_array("GeneTraits", "NameProperty", [self.__get_gene_trait_bytes(trait, level, save)])
        else:
            new_genes = [self.__get_gene_trait_bytes(ArkDinoTrait.from_string(t), int(t.split("[")[1][:-1]), save) for t in self.gene_traits]
            self.binary.set_property_position("GeneTraits")
            self.binary.replace_array("GeneTraits", "NameProperty", new_genes)
        
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)
    