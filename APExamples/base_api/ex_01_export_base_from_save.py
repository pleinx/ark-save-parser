from pathlib import Path

from arkparse import AsaSave, MapCoords
from arkparse.enums import ArkMap
from arkparse.api import BaseApi
from arkparse.ftp.ark_ftp_client import ArkFtpClient

# retrieve the save file (can also retrieve it from a local path)
path = ArkFtpClient.from_config('../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd())
location = MapCoords(80, 75.5) # add the coordinates here
size = 1 # add the size here (in map coordinates)
storage_path = Path.cwd() / 'example' # add the path where the base should be stored

SAVE = AsaSave(path)
bApi = BaseApi(SAVE, ArkMap.ABERRATION)

base_path = storage_path
base = bApi.get_base_at(location, radius=size)
base.store_binary(base_path)