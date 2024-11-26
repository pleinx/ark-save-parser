from pathlib import Path
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.classes.dinos import Dinos
from arkparse.logging import ArkSaveLogger
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.parsing.ark_property import ArkProperty

bp = Dinos.reaper_queen
save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)

bps = [
    # r"/Game/PrimalEarth/CoreBlueprints/PlayerCharacterStatusComponent_BP.PlayerCharacterStatusComponent_BP_C",
    # r"/Game/PrimalEarth/CoreBlueprints/PlayerControllerBlueprint.PlayerControllerBlueprint_C",
    r"/Game/PrimalEarth/CoreBlueprints/PlayerPawnTest_Female.PlayerPawnTest_Female_C",
    r"/Game/PrimalEarth/CoreBlueprints/PlayerPawnTest_Male.PlayerPawnTest_Male_C",
]

config = GameObjectReaderConfiguration(
    blueprint_name_filter=lambda name: name is not None and "PrimalItem_WeaponEmptyCryopod_C" in name,
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

print_all = True
print_values = []
print_obj = False
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
