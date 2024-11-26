import logging
from uuid import UUID
from typing import List

from arkparse.parsing.ark_property import ArkProperty
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.objects.saves.game_objects.equipment.saddle import Saddle
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.game_objects.misc.inventory_item import InventoryItem

class EmbeddedCryopodData:
    class Item:
        DINO_AND_STATUS = 0
        SADDLE = 1
        COSTUME = 2
        UNKNOWN = 3

    data_byte_arrays: List[bytes]
    
    def __init__(self, data_arrays: List[ArkProperty]):
        self.data_byte_arrays = [[] if data.value is None else bytes(data.value) for data in data_arrays]

    def __unembed__(self, item):
        if item > len(self.data_byte_arrays):
            return None

        elif item == self.Item.DINO_AND_STATUS:
            bts = self.data_byte_arrays[0]
            if len(bts) != 0:
                parser: ArkBinaryParser = ArkBinaryParser.from_deflated_data(bts)
                objects: List[ArkGameObject] = []
                nr_of_obj = parser.read_uint32()
                for _ in range(nr_of_obj):
                    objects.append(ArkGameObject(binary_reader=parser, from_custom_bytes=True))

                for obj in objects:
                    obj.read_props_at_offset(parser)

                return objects[0], objects[1]

            return None, None

        elif item <= self.Item.UNKNOWN:
            bts = self.data_byte_arrays[item]
            if len(bts) != 0:
                parser = ArkBinaryParser(bts)
                parser.validate_uint32(6)
                obj = ArkGameObject(binary_reader=parser, no_header=True)
        
        return None
    
    def get_dino_obj(self):
        return self.__unembed__(self.Item.DINO_AND_STATUS)
    
    def get_saddle_obj(self):
        return self.__unembed__(self.Item.SADDLE)

class Cryopod(InventoryItem): 
    embedded_data: EmbeddedCryopodData
    dino: TamedDino
    saddle: Saddle
    costume: any

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None, save: AsaSave = None):
        super().__init__(uuid, binary, save)
        self.embedded_data = EmbeddedCryopodData(self.object.get_array_property_value("ByteArrays"), [])

        if len(self.embedded_data) != 4 and len(self.embedded_data) != 0:
            raise ValueError("Expected 4 or no byte arrays, got ", len(self.embedded_data))
        
        dino_obj, status_obj = self.embedded_data.get_dino_obj()
        self.dino = TamedDino.from_object(dino_obj, status_obj)
        self.saddle = Saddle.from_object(self.embedded_data.get_saddle_obj())
        self.costume = None     
