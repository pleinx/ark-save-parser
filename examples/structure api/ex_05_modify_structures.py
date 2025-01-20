from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave, MapCoords
from arkparse.api import StructureApi, PlayerApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

# Same as ex 02
map = ArkMap.ABERRATION
lat = 70 # add the coordinates here
lon = 30 # add the coordinates here
structure_api = StructureApi(save)
structures: Dict[UUID, StructureWithInventory] = structure_api.get_at_location(map, MapCoords(lat, lon), radius=1)
with_connected = structure_api.get_connected_structures(structures)

new_owner_id = 0 # add the new owner id here
new_max_health = 10000000.0

owner = PlayerApi(save=save, map=map, ftp_config=Path("../../ftp_config.json")).get_as_owner(new_owner_id, PlayerApi.OwnerType.OBJECT)
structure_api.modify_structures(with_connected, new_owner=owner, new_max_health=new_max_health)

# alternatively, if you have an ftp client to upload the save file to:
# structure_api.modify_structures(with_connected, new_owner=owner, new_max_health=new_health, ftp_client=ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION))
