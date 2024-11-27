from pathlib import Path
import json

from arkparse.api.structure_api import StructureApi
from arkparse.api.player_api import PlayerApi, ArkMaps
from arkparse.objects.saves.game_objects.misc.object_owner import ObjectOwner
from arkparse.objects.saves.game_objects.structures.placed_structure import SimpleStructure

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes.placed_structures import PlacedStructures
from arkparse.logging import ArkSaveLogger

ArkSaveLogger.temp_file_path = Path.cwd()


path = Path.cwd() / "test_saves" / "server.ark"
ftp = Path.cwd().parent / "ftp_config.json"

save = AsaSave(path, read_only=False)
structure_api = StructureApi(save)
# player_api = PlayerApi(ftp_config=ftp, map=ArkMaps.ABERRATION, save=save)

structures = structure_api.get_by_class(PlacedStructures.stone.floor)

print(f"Found {len(structures)} structures\n")

bobette_owned = {}
for key, structure in structures.items():
    if structure.owner.player_name == "Bobette":
        bobette_owned[structure.object.uuid] = structure
        print(structure.to_string_complete())
        print("\n")
        break

new_owner = ObjectOwner.from_profile(276678343, "123", "Tribe of 123")

bobette_owned = structure_api.get_connected_structures(bobette_owned)
print("Connected building structure count: ", len(bobette_owned))

if bobette_owned is not None:
    print("Replacing owner to '123':")
    structure_api.transfer_ownership(new_owner, bobette_owned)
    print("Done")

    print("\nReparsing binary")
    for key, structure in bobette_owned.items():
        structure : SimpleStructure = structure
        new_structure = SimpleStructure(key, structure.binary)
        print(structure.to_string_complete())
        print("\n")

save.store_db(Path.cwd() / "modified.ark")
    