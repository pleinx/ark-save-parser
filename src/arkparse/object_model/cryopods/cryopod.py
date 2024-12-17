import logging
from uuid import UUID
from typing import List

from arkparse.parsing.ark_property import ArkProperty
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.equipment.saddle import Saddle
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.inventory_item import InventoryItem

class EmbeddedCryopodData:
    class Item:
        DINO_AND_STATUS = 0
        SADDLE = 1
        COSTUME = 2
        UNKNOWN = 3

    data_byte_arrays: List[bytes]
    
    def __init__(self, data_arrays: List[ArkProperty]):
        self.data_byte_arrays = [[] if data.value is None else bytes(data.value) for data in data_arrays]

        if len(self.data_byte_arrays) != 4 and len(self.data_byte_arrays) != 0:
            raise ValueError("Expected 4 or no byte arrays, got ", len(self.data_byte_arrays))

    def __unembed__(self, item):
        if item > (len(self.data_byte_arrays) - 1):
            if item == self.Item.DINO_AND_STATUS:
                return None, None
            
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

    def __init__(self, uuid: UUID = None, binary: ArkBinaryParser = None):
        super().__init__(uuid, binary)
        self.dino = None
        self.saddle = None
        self.costume = None
        self.embedded_data = EmbeddedCryopodData(self.object.get_array_property_value("ByteArrays", default=[]))
        
        dino_obj, status_obj = self.embedded_data.get_dino_obj()
        
        if dino_obj is not None and status_obj is not None:
            self.dino = TamedDino.from_object(dino_obj, status_obj, self)
            self.dino.location.in_cryopod = True

        saddle_obj = self.embedded_data.get_saddle_obj()
        if saddle_obj is not None:
            self.saddle = Saddle.from_object(saddle_obj)

        self.costume = None   

    def is_empty(self):
        return self.dino is None 

    def __str__(self):
        if self.is_empty():
            return "Cryopod(empty)"
        
        return "Cryopod(dino={}, lv={}, saddle={})".format(self.dino.get_short_name(), self.dino.stats.current_level, "no saddle" if self.saddle is None else self.saddle.get_short_name())
