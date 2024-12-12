from pathlib import Path

from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap, ArkStat
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes.dinos import Dinos
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino

save_path = Path.cwd() / "Aberration_WP.ark"            # replace with path to your save file
save = AsaSave(save_path)                               # load the save file
dino_api = DinoApi(save)                                # create a DinoApi object

dino, value, stat = dino_api.get_best_dino_for_stat(
    classes=[Dinos.rock_drake],
    only_tamed=True,
    stat=ArkStat.WEIGHT,
    base_stat=True
)   # get the dino with the highest stat

if dino is None:
    print("No tamed Rock Drake found")
    exit()

dino: TamedDino = dino
print(f"The dino with the highest base weight is {dino.get_short_name()} with {value} points")   # print the dino with the highest stat
print(f"Location: {dino.location.as_map_coords(ArkMap.ABERRATION)}")                        # print the location of the dino
print(f"Level: {dino.stats.current_level}")                                                 # print the level of the dino
print(f"Owner: {dino.owner}")                                                               # print the owner of the dino