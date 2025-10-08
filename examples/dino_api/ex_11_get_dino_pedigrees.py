from typing import Dict, List
from uuid import UUID
from pathlib import Path
import random

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api import DinoApi, PlayerApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.pedigree import Pedigree
from arkparse.utils import _TEST_FILE_ASTRAEOS_WP

save_path = _TEST_FILE_ASTRAEOS_WP
save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd())
print(f"Loading save file: {save_path}")

save = AsaSave(save_path) # load the save file
dino_api = DinoApi(save) # using the dino API as an example     
player_api = PlayerApi(save) # using the player API as an example   
tamed = dino_api.get_all_tamed()
print(f"Total tamed dinos: {len(tamed)}")

random_tamed = list(tamed.values())[random.randint(0, len(tamed)-1)]

pedigrees: List[Pedigree] = dino_api.get_all_pedigrees(player_api, min_generations=2)
# pedigrees: List[Pedigree] = [Pedigree(random_tamed, dino_api, player_api)]

largest = None
for pedigree in pedigrees:
    if largest is None or len(pedigree.entries) > len(largest.entries):
        largest = pedigree

largest_pedigree = largest

largest_pedigree.visualize_as_html(f"largest_pedigree_{largest_pedigree.dino_type}.html", largest_pedigree.dino_type)
largest_pedigree.print_tree()
