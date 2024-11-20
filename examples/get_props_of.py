from pathlib import Path
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.classes.dinos import Dinos
from arkparse.logging import ArkSaveLogger
from arkparse.objects.saves.game_objects.abstract_game_object import AbstractGameObject
from arkparse.parsing import ArkBinaryParser

bp = Dinos.reaper_queen
save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)

config = GameObjectReaderConfiguration(
    blueprint_name_filter=lambda name: name is not None and "Resources/PrimalItemResource" in name,
)

objects = save.get_game_objects(config)

unique_props = set()
prop_counts = {}

for obj in objects.values():
    props = obj.get_properties()
    for prop in props:
        unique_props.add(prop)
        prop_counts[prop] = prop_counts.get(prop, 0) + 1

    if obj.get_property_value("bIsInitialItem"):
        print(obj.blueprint)

print("Properties:")
print(unique_props)

print("\nProperty counts:")
print(prop_counts)

ArkSaveLogger.temp_file_path = Path.cwd()

# ArkSaveLogger.enable_debug = True
# binary = save.get_game_obj_binary(list(objects.keys())[0]) #list(objects.keys())[0])
# parser = ArkBinaryParser(binary, save.save_context)
# ArkSaveLogger.set_file(parser, "debug.bin")
# o = AbstractGameObject(list(objects.keys())[0], bp, parser)
# ArkSaveLogger.open_hex_view(True)




