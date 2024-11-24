from arkparse.objects.saves.asa_save import AsaSave
from arkparse.logging import ArkSaveLogger
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.parsing import ArkBinaryParser
from arkparse.objects.saves.game_objects.abstract_game_object import AbstractGameObject

from pathlib import Path
from typing import List

save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)

bps = [#r"/Cryopods/Cryopods/PrimalItem_WeaponEmptyCryopod_Mod.PrimalItem_WeaponEmptyCryopod_Mod_C",
    #    , r"/Cryopods/Cryopods_Singleton_Auto7.Cryopods_Singleton_C", 
       r"/Game/Extinction/CoreBlueprints/Weapons/PrimalItem_WeaponEmptyCryopod.PrimalItem_WeaponEmptyCryopod_C",]
    #    r"/Cryopods/Items/CryoGun/PrimalItemWeapon_CryoGun_Mod.PrimalItemWeapon_CryoGun_Mod_C",
    #    r"/Cryopods/Structures/CryoTerminal/PrimalItemStructure_CryoTerminal_Mod.PrimalItemStructure_CryoTerminal_Mod_C"]

config = GameObjectReaderConfiguration(
    blueprint_name_filter=lambda name: name in bps
)

# ArkSaveLogger.enable_debug = True
ArkSaveLogger.temp_file_path = Path.cwd() / "test_saves" 
objects = save.get_game_objects(config)

for key, obj in objects.items():
    print("\nObject: ", key, "Class: ", obj.blueprint)
    bytearrs = obj.get_array_property_value("ByteArrays")
    print(bytearrs)
    if len(bytearrs) != 4:
        if len(bytearrs) != 0:
            raise ValueError("Expected 4 or no byte arrays, got ", len(bytearrs))
    else:
        if bytearrs[0].value is not None:
            reader = ArkBinaryParser.from_deflated_data(bytearrs[0].value)
            ArkSaveLogger.set_file(reader, "debug.bin")
            
            objects: List[AbstractGameObject] = []
            nr_of_obj = reader.read_uint32()
            for _ in range(nr_of_obj):
                game_object = objects.append(AbstractGameObject(binary_reader=reader, from_custom_bytes=True))

            for obj in objects:
                obj.read_props_at_offset(reader)

        if bytearrs[1].value is not None:
            asbytes = bytes(bytearrs[1].value)
            reader = ArkBinaryParser(asbytes)
            ArkSaveLogger.set_file(reader, "debug.bin")
            ArkSaveLogger.byte_buffer = reader
            ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view(True)

