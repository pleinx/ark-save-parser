from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import TamedDino

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd()) # or download the save file from an FTP server
save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

dinos: Dict[UUID, TamedDino] = dino_api.get_all()

trait_set = set()

for key, dino in dinos.items():
    print(dino.gene_traits)
    for trait in dino.gene_traits:
        trait_set.add(trait[:-3])

with open("traits.txt", "w") as f:
    for trait in trait_set:
        f.write(trait + "\n")
