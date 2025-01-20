from pathlib import Path

from arkparse import AsaSave
from arkparse.parsing.struct.actor_transform import ActorTransform, ArkVector
from arkparse.enums import ArkMap
from arkparse.api import BaseApi
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.object_model.bases.base import Base

# retrieve the save file (can also retrieve it from a local path)
map_ = ArkMap.ABERRATION
path = ArkFtpClient.from_config('../ftp_config.json', map_).download_save_file(Path.cwd())
import_location = ActorTransform(ArkVector(128348, 2888, 59781)) # add the coordinates here (Get them using the console in game)
size = 1 # add the size here (in map coordinates)
base_storage_path = Path.cwd() / 'example' # add the path where the base is stored
save_storage_path = Path.cwd() / 'example_modified_save' # add the path where the save is stored

SAVE = AsaSave(path)
bApi = BaseApi(SAVE, map_)

base: Base = bApi.import_base(base_storage_path, import_location)
SAVE.store_db(save_storage_path)