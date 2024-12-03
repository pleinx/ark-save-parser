from pathlib import Path
from arkparse.api.structure_api import StructureApi
from arkparse.api.player_api import PlayerApi, FtpArkMap, ArkFtpClient
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap, ArkStat
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino, Dino
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes.placed_structures import PlacedStructures
from arkparse.classes.dinos import Dinos
from arkparse.utils import draw_heatmap

save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)
structure_api = StructureApi(save)
dino_api = DinoApi(save)
player_api = PlayerApi(Path("../ftp_config.json"), FtpArkMap.ABERRATION, save=save)
b = None

stat_limit = 35
dinos = dino_api.get_all_filtered(tamed=False, 
                                  stat_minimum=stat_limit, 
                                  level_upper_bound=150, 
                                  stats=[ArkStat.HEALTH, ArkStat.MELEE_DAMAGE])

for key, dino in dinos.items():
    dino : Dino = dino
    s = f"{dino}: {dino.location.as_map_coords(ArkMap.ABERRATION)}"
    stats = dino.stats.get_of_at_least(limit)
    for stat in stats:
        s += f" {dino.stats.stat_to_string(stat)}"
    print(s)

heatmap = dino_api.create_heatmap(dinos=dinos)
draw_heatmap(heatmap, ArkMap.ABERRATION)