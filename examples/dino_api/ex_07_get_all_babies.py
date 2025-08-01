from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos import TamedBaby, Baby, Dino

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd()) # or download the save file from an FTP server
save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

dinos: Dict[UUID, Dino] = dino_api.get_all_babies(include_wild=True)

wild_baby_count = sum(1 for dino in dinos.values() if isinstance(dino, Baby))
tamed_baby_count = sum(1 for dino in dinos.values() if isinstance(dino, TamedBaby))

print(f"Total Wild Babies: {wild_baby_count}")
print(f"Total Tamed Babies: {tamed_baby_count}")

# Display details of all babies
print("Details of tamed babies:")
for dino in dinos.values():
    if isinstance(dino, TamedBaby):
        print(f"Tamed Baby: {dino.get_short_name()}, Stage: {dino.stage.value}, Matured: {dino.percentage_matured:.2f}%")