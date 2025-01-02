from pathlib import Path

from arkparse.utils import draw_heatmap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave

save_path = Path.cwd() / "test_saves" / "server.ark"    # replace with path to your save file
save = AsaSave(save_path)                               # load the save file
dino_api = DinoApi(save)                                # create a DinoApi object

dinos = dino_api.get_all_filtered(tamed=True)           # only consider tamed dinos

heatmap = dino_api.create_heatmap(dinos=dinos)          # create a heatmap of the dinos
draw_heatmap(heatmap, ArkMap.ABERRATION)                # draw the heatmap for the Aberration map