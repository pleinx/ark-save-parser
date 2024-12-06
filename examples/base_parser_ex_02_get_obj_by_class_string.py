from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from arkparse.parsing import GameObjectReaderConfiguration

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../ftp_config.json"), FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

# Get object by UUID
# Example, can be part of a string or full class string
class_ = "StorageBox"
config = GameObjectReaderConfiguration(
    blueprint_name_filter=lambda name: name is not None and class_ in name)  # Create filter
# Create list of generic Ark objects
objects: Dict[UUID, ArkGameObject] = save.get_game_objects(config)

for obj in objects.values():
    print(f"Found object with {class_} in its classname: {obj.blueprint}")
    obj.print_properties()
