from pathlib import Path
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../ftp_config.json"), FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

# Get object by UUID
uuid = UUID("eb102031-a1c0-cc44-9069-7783ec31a851")         # Example UUID
obj: ArkGameObject = save.get_game_object_by_id(
    uuid)       # Create generic Ark object

if obj is not None:
    print(f"Found object with UUID {uuid}: {obj.blueprint}")
    obj.print_properties()
