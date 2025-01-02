from pathlib import Path

from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.object_model.ark_game_object import ArkGameObject

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

obj: ArkGameObject = save.get_game_objects()

print(f"Parsed {len(obj)} game objects from the save file.")
