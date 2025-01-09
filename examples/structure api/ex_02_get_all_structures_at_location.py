from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave, MapCoords
from arkparse.api import StructureApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

map = ArkMap.ABERRATION
lat = 70 # add the coordinates here
lon = 30 # add the coordinates here

structure_api = StructureApi(save)

structures: Dict[UUID, StructureWithInventory] = structure_api.get_at_location(map, MapCoords(lat, lon), radius=1)

# you could expand this with all connected structures as well in case half a base was included in the radius:
with_connected = structure_api.get_connected_structures(structures)
