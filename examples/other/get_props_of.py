from pathlib import Path
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.classes import Classes
from arkparse.logging import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.parsing.ark_property import ArkProperty
from arkparse.object_model.misc.inventory import Inventory
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap

save_path = Path.cwd() / "test_saves" / "original.ark"
save_path = ArkFtpClient.from_config(Path("../ftp_config.json"), FtpArkMap.ABERRATION).download_save_file(Path.cwd())

save = AsaSave(save_path)

bps = [Classes.equipment.weapons.advanced.compound_bow]

config = GameObjectReaderConfiguration(
    blueprint_name_filter=lambda name: name is not None and name in bps,
)

ArkSaveLogger.enable_debug = True
objects = save.get_game_objects(config)

unique_props = set()
prop_counts = {}

for obj in objects.values():
    props = obj.get_properties()
    for prop in props:
        unique_props.add(prop)
        prop_counts[prop] = prop_counts.get(prop, 0) + 1

print("Properties:")
print(unique_props)

print("\nProperty counts:")
print(prop_counts)

print_all = True
print_values = []
print_obj = True
avoid_values = ["ByteArrays", "CustomDataBytes"]

for prop in unique_props:
    if prop.split('(')[0] in print_values or (print_all and prop.split('(')[0] not in avoid_values):
        print(f"\nProperty: {prop}")
        for obj in objects.values():
            if prop in obj.get_properties():
                if not print_obj:
                    prop : ArkProperty = prop
                    print(f"Object: {obj.blueprint}, Value: {obj.get_property_value(prop.split('(')[0])}")
                else:
                    print(f"\nObject: {obj.blueprint}")
                    obj.print_properties()

ArkSaveLogger.temp_file_path = Path.cwd()
