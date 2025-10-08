from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos import TamedDino
from arkparse.classes.dinos import Dinos
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap


save_path = Path.cwd() / "test_saves" / "server.ark" # replace with path to your save file

# Or get your save file from an FTP server
save_path  = ArkFtpClient.from_config("../../ftp_config.json", ArkMap.RAGNAROK).download_save_file(Path.cwd()) 

save = AsaSave(save_path)   # load the save file
dino_api = DinoApi(save)    # create a DinoApi object

dinos: Dict[UUID, TamedDino] = dino_api.get_all_filtered(tamed=True,
                                  class_names=[Dinos.flyers.wyverns.lightning]
)      

# print the output
for key, dino in dinos.items():
    dino : TamedDino = dino
    if dino.tamed_name == "ThisIsMyWyvern":  # replace with the name of the dino you want to remove (or use other identiying features, like owner, location, etc.)
        dino.remove_from_save()

        print(f"Removed {dino} from save file")
        break

save.store_db(Path.cwd() / "dino_removed.ark")