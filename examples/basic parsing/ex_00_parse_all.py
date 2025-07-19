from pathlib import Path
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.object_model.ark_game_object import ArkGameObject

from arkparse.logging import ArkSaveLogger

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../../ftp_config.json"), ArkMap.RAGNAROK).download_save_file(Path.cwd())
save = AsaSave(save_path)

ArkSaveLogger.enable_debug = True
save.get_game_object_by_id(UUID("84d0be30-5678-2640-a1f5-3596cd5c23cb"))
ArkSaveLogger.enable_debug = False

obj: ArkGameObject = save.get_game_objects()

print(f"Parsed {len(obj)} game objects from the save file.")
