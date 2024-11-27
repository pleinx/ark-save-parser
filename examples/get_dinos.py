from pathlib import Path
import json

from arkparse.enums.ark_map import ArkMap
from arkparse.struct.actor_transform import ActorTransform, MapCoords
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.api.dino_api import DinoApi
from arkparse.classes.dinos import Dinos
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino


class_ = None
lower_lvl = None
upper_lvl = None
tamed = True

save_path = Path.cwd() / "test_saves" / "Aberration_WP.ark"
save = AsaSave(save_path)
dApi = DinoApi(save)

dinos = dApi.get_all_filtered(lower_lvl, upper_lvl, class_, tamed)

print("Dinos:")
if class_ is not None:
    print(f"   - Class = {class_}")
if lower_lvl is not None:
    print(f"   - Lower level = {lower_lvl}")
if upper_lvl is not None:
    print(f"   - Upper level = {upper_lvl}")
if tamed is not None:
    print(f"   - Tamed = {tamed}")

print("\nBy level:")
print(json.dumps(dApi.count_by_level(dinos), indent=4))

print("\nBy class:")
print(json.dumps(dApi.count_by_class(dinos), indent=4))

print("\n")
for key, dino in dinos.items():
    if isinstance(dino, TamedDino) and dino.cryopod is not None:
        print(f"{key}: location = Cryopod")
    else:
        print(f"{key}: location = {dino.location.as_map_coords(ArkMap.ABERRATION)}")

for key, dino in dinos.items():
    dino.object.print_properties()
