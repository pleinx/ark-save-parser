from arkparse.objects.saves.asa_save import AsaSave
from arkparse.logging import ArkSaveLogger
from arkparse.parsing import GameObjectReaderConfiguration

from pathlib import Path

save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)

bps = [r"/Cryopods/Cryopods/PrimalItem_WeaponEmptyCryopod_Mod.PrimalItem_WeaponEmptyCryopod_Mod_C",
    #    , r"/Cryopods/Cryopods_Singleton_Auto7.Cryopods_Singleton_C", 
       r"/Game/Extinction/CoreBlueprints/Weapons/PrimalItem_WeaponEmptyCryopod.PrimalItem_WeaponEmptyCryopod_C",]
    #    r"/Cryopods/Items/CryoGun/PrimalItemWeapon_CryoGun_Mod.PrimalItemWeapon_CryoGun_Mod_C",
    #    r"/Cryopods/Structures/CryoTerminal/PrimalItemStructure_CryoTerminal_Mod.PrimalItemStructure_CryoTerminal_Mod_C"]

config = GameObjectReaderConfiguration(
    blueprint_name_filter=lambda name: name in bps
)

ArkSaveLogger.enable_debug = True
ArkSaveLogger.temp_file_path = Path.cwd() / "test_saves" 
objects = save.get_game_objects(config)

for key, obj in objects.items():
    print("\nObject: ", key, "Class: ", obj.blueprint)
    print(obj.print_properties())