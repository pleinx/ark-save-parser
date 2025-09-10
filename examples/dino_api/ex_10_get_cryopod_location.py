from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos import TamedDino
from arkparse import Classes

# save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd())   # or download the save file from an FTP server
save_path = Path.cwd() / "Ragnarok_WP.ark"                                                               # or load it from a local path
save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

wild_tamables: Dict[UUID, TamedDino] = dino_api.get_all_in_cryopod()

for dino in wild_tamables.values():
    print(f"Dino {dino.get_short_name()} (owned by tribe {dino.owner.target_team}) is in a cryopod at {dino.location}")