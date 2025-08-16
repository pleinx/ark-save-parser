from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos import Dino
from arkparse.helpers.dino.is_wild_tamed import is_wild_tamed

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd())   # or download the save file from an FTP server
save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

for dino in dino_api.get_all_tamed().values():
    if (is_wild_tamed(dino)):
        print(f"A wild tamed dino was found: {dino.get_short_name()} with level {dino.stats.current_level}")