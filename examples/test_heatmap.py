from pathlib import Path
from arkparse.api.structure_api import StructureApi
from arkparse.api.player_api import PlayerApi, FtpArkMap, ArkFtpClient
from arkparse.api.dino_api import DinoApi
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes.placed_structures import PlacedStructures
from arkparse.classes.dinos import Dinos

save_path = Path.cwd() / "test_saves" / "Aberration_WP.ark"
save = AsaSave(save_path)
structure_api = StructureApi(save)
dino_api = DinoApi(save)
# player_api = PlayerApi(Path("../ftp_config.json"), FtpArkMap.ABERRATION, save=save)
b = None
# b = player_api.get_as_owner(PlayerApi.OwnerType.OBJECT, ue5_id="0002dbd6e6a148378b36823f9720f651")

# buildings = PlacedStructures.metal.all_bps + PlacedStructures.stone.all_bps + PlacedStructures.wood.all_bps + \
#             PlacedStructures.thatch.all_bps + PlacedStructures.tek.all_bps + PlacedStructures.crafting.all_bps + \
#             PlacedStructures.turrets.all_bps

# turrets = PlacedStructures.turrets.all_bps

# metal = PlacedStructures.metal.all_bps
 
# structure_api.create_heatmap(classes=buildings, owner=b)

dino_api.create_heatmap(classes=Dinos.reaper_queen)
