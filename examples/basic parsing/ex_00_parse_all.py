from pathlib import Path
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.object_model.ark_game_object import ArkGameObject

from arkparse.logging import ArkSaveLogger

save_path = Path("C:\\Users\\Vincent\\Downloads\\ASV\\Ragnarok_WP\\Ragnarok_WP.ark")
# retrieve the save file (can also retrieve it from a local path)
# save_path = ArkFtpClient.from_config(
#     Path("../../ftp_config.json"), ArkMap.RAGNAROK).download_save_file(Path.cwd())
# save_path = Path.cwd() / "Ragnarok_WP.ark"
save = AsaSave(save_path)
obj: ArkGameObject = save.get_game_objects()

print(f"Parsed {len(obj)} game objects from the save file.")
