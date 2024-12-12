from pathlib import Path
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api.player_api import PlayerApi
from arkparse.api.dino_api import DinoApi
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino
from arkparse.parsing import GameObjectReaderConfiguration

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.logging import ArkSaveLogger

ArkSaveLogger.temp_file_path = Path.cwd()

path = Path.cwd() / "Aberration_WP.ark"
save = AsaSave(path, read_only=False)
dino_api = DinoApi(save)

ArkSaveLogger.enable_debug = True
charles = dino_api.get_by_uuid(UUID("45c5eaee-f017-a24e-8448-f76b53bf1620"))

# Get Charles LeCrab
print(f"Found Charles LeCrab: {charles.get_short_name()}")
charles.object.print_properties()

config = GameObjectReaderConfiguration(
    blueprint_name_filter = lambda name: name == "/Game/Aberration/CoreBlueprints/DinoCharacterStatusComponent_BP_CaveCrab.DinoCharacterStatusComponent_BP_CaveCrab_C",
)

# obj = save.get_game_objects(config)
# print(len(obj))

# for obj in obj.values():
#     print("\n")
#     obj.print_properties()
#     print("\n")

print("\nHis stats:")
charles.stats.object.print_properties()
