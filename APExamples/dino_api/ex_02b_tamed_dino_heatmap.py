from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.utils import draw_heatmap
from arkparse.api.dino_api import DinoApi, TamedDino, MapCoords
from arkparse.logging import ArkSaveLogger
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd()) # or download the save file from an FTP server
save = AsaSave(save_path)                               # load the save file
dino_api = DinoApi(save)                                # create a DinoApi object

ArkSaveLogger.enable_debug = True  # Enable debug logging
obj = save.get_game_object_by_id(UUID("8e22ad59-7b76-3a4a-b223-c60311f2bd7a")) 
ArkSaveLogger.enable_debug = False

dinos: Dict[UUID, TamedDino] = dino_api.get_all_filtered(tamed=True)           # only consider tamed dinos

for dino in dinos.values():                  # iterate over all dinos
    print(f"{dino.owner}, {dino.tamed_name}, {dino.location} ({dino.location.as_map_coords(ArkMap.RAGNAROK)})")  # print owner, name, species, level, and location

heatmap = dino_api.create_heatmap(map=ArkMap.RAGNAROK, dinos=dinos)          # create a heatmap of the dinos
draw_heatmap(heatmap, ArkMap.RAGNAROK)                # draw the heatmap for the Aberration map