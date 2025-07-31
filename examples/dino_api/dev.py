from pathlib import Path
from uuid import UUID
from typing import Dict, List

from arkparse.api.dino_api import DinoApi, TamedDino, Dino
from arkparse.logging import ArkSaveLogger
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.object_model.ark_game_object import ArkGameObject

# save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd()) # or download the save file from an FTP server
save_path = Path("C:/data/personal/git/ark-save-parser/tests/test_data/set_1/Astraeos_WP/Astraeos_WP.ark")  # Or use a local path
save = AsaSave(save_path)                               # load the save file
dino_api = DinoApi(save)                                # create a DinoApi object

dinos: Dict[UUID, Dino] = dino_api.get_all()

dino_props = set()
status_props = set()

babies: List[Dino] = []

for dino in dinos.values():
    if dino.object.get_property_value("bIsBaby", False):
        babies.append(dino)

for dino in babies:
    for prop in dino.object.properties:
        dino_props.add(prop.name)
    for prop in dino.stats.object.properties:
        status_props.add(prop.name)

print(f"Total babies found: {len(babies)}")
print(f"Total baby properties found: {len(dino_props)}")
print(f"Total baby status properties found: {len(status_props)}")

print("Baby properties:")
for prop in dino_props:
    print(f" - {prop}")

print("Baby status properties:")
for prop in status_props:
    print(f" - {prop}")



print(f"Total baby dinos found: {len(babies)}")

log_props = {
    ""
}

imprints = set()
ages = set( )


