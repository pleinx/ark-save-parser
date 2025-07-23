from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.api.dino_api import DinoApi, TamedDino, MapCoords
from arkparse.logging import ArkSaveLogger
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing.struct.actor_transform import ActorTransform

BASE_STORAGE_PATH = Path.cwd() / 'temp' / 'exports'

def create_folder(folder: str) -> None:
    """Create a folder if it does not exist."""
    path = BASE_STORAGE_PATH / folder
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

# save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd()) # or download the save file from an FTP server
save_path = Path.cwd() / 'Ragnarok_WP.ark'              # or use a local save file
save = AsaSave(save_path)                               # load the save file
dino_api = DinoApi(save)                                # create a DinoApi object

dinos: Dict[UUID, TamedDino] = dino_api.get_all_filtered(tamed=True, level_lower_bound=1000)           # only consider tamed dinos

for dino in dinos.values():                  # iterate over all dinos
    print(f"{dino.owner}, {dino.tamed_name}, {dino.location} ({dino.location.as_map_coords(ArkMap.RAGNAROK)})")  # print owner, name, species, level, and location
    name = dino.tamed_name if dino.tamed_name else "Unknown"
    create_folder(name)  # create a folder for the tamed dino if it does not exist
    dino.store_binary(BASE_STORAGE_PATH / name)

dino: TamedDino = list(dinos.values())[0]
print("Binary:")
dino.binary.structured_print()
print(f"Props:")
dino.object.print_properties()
print(f"Stats:")
dino.stats.object.print_properties()

at = save.save_context.get_actor_transform(dino.object.uuid)
if at:
    print(f"Actor Transform for {dino.tamed_name}: {at}")
else:
    print(f"No Actor Transform found for {dino.tamed_name}")

ArkSaveLogger.enable_debug = True
ArkSaveLogger.suppress_warnings = False
new_loc = MapCoords(77.77, 77.77).as_actor_transform(ArkMap.RAGNAROK)
dino.set_location(new_loc, save)
dino.binary.structured_print()
new_vector = dino.object.get_property_value("SavedBaseWorldLocation")
print(ActorTransform(vector=new_vector).as_map_coords(ArkMap.RAGNAROK))
ArkSaveLogger.enable_debug = True