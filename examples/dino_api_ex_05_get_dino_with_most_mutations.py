from pathlib import Path

from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino

save_path = Path.cwd() / "Aberration_WP.ark"            # replace with path to your save file
save = AsaSave(save_path)                               # load the save file
dino_api = DinoApi(save)                                # create a DinoApi object

dinos = dino_api.get_all_tamed()                        # print the owner of the dino

if dinos is None:
    print("No tamed dinos found")
    exit()

most_mutations: TamedDino = None
for dino in dinos.values():
    dino: TamedDino = dino
    curr = 0 if most_mutations is None else most_mutations.stats.get_total_mutations()
    if most_mutations is None or (dino.stats.get_total_mutations() > curr):
        most_mutations = dino

if most_mutations is None:
    print("No dinos with mutations found")
    exit()

print(f"The dino with the most mutations is a {most_mutations.get_short_name()} with {int(most_mutations.stats.get_total_mutations())} mutations") # print the dino with the highest stat
print(f"Location: {most_mutations.location.as_map_coords(ArkMap.ABERRATION)}")                                                                     # print the location of the dino
print(f"Level: {most_mutations.stats.current_level}")                                                                                              # print the level of the dino
print(f"Owner: {most_mutations.owner}")                                                                                                            # print the owner of the dino