from pathlib import Path

from arkparse.utils import draw_heatmap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap, ArkStat
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import Dino
from arkparse.classes.dinos import Dinos
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap


save_path = Path.cwd() / "test_saves" / "server.ark" # replace with path to your save file
save_path  = ArkFtpClient.from_config("../ftp_config.json", FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)                            # load the save file
dino_api = DinoApi(save)                             # create a DinoApi object

limit = 0 # set the limit for the stats
dinos = dino_api.get_all_filtered(tamed=False,                                  # only consider wild dinos
                                  stat_minimum=limit,                           # set the limit
                                  class_names=[Dinos.alpha_reaper_king, Dinos.reaper_queen],
                                  level_upper_bound=150,                        # only consider dinos up to level 150 (no wild wyverns / drakes)
                                  stats=[ArkStat.HEALTH, ArkStat.MELEE_DAMAGE, ArkStat.FOOD]) # only consider dinos with at least 35 points in health or melee damage (if not assigned, all stats are considered)

for key, dino in dinos.items():
    dino : Dino = dino
    s = f"{dino}: {dino.location.as_map_coords(ArkMap.ABERRATION)}"
    stats = dino.stats.get_of_at_least(limit)
    for stat in stats:
        s += f" {dino.stats.stat_to_string(stat)}"
    print(s) # print the dino's name, location, and stats above the limits

# example print output:
# Dino(type=Arthro_Character_BP_Aberrant, lv=135): (92.06, 69.56) melee_damage=35
# Dino(type=Dimorph_Character_BP_Aberrant, lv=140): (60.96, 41.45) health=35
# Dino(type=Arthro_Character_BP_Aberrant, lv=140): (91.97, 50.07) melee_damage=36
# Dino(type=Arthro_Character_BP_Aberrant, lv=150): (82.31, 68.03) health=39 food=35 melee_damage=35

heatmap = dino_api.create_heatmap(dinos=dinos) # create a heatmap of the dinos
draw_heatmap(heatmap, ArkMap.ABERRATION)       # draw the heatmap for the Aberration map