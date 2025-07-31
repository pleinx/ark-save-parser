from pathlib import Path

from arkparse import AsaSave
from arkparse.parsing.struct.actor_transform import ActorTransform, ArkVector
from arkparse.enums import ArkMap
from arkparse.api import BaseApi
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.object_model.bases.base import Base

def ex_02a_import_base_at_location(save_path: AsaSave, map: ArkMap, import_location: ActorTransform, base_storage_path: Path, save_storage_path: Path):
    """
    Example to import a base from a save file at a specific location.
    """
    if not Path.cwd().exists():
        raise FileNotFoundError(f"Current working directory does not exist at {Path.cwd()}")
    
    SAVE = AsaSave(save_path)
    bApi = BaseApi(SAVE, map)
    base: Base = bApi.import_base(base_storage_path, import_location)
    SAVE.store_db(save_storage_path)


if __name__ == '__main__':
    path = ArkFtpClient.from_config('../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd())
    ex_02a_import_base_at_location(
        path, 
        ArkMap.ABERRATION, 
        ActorTransform(ArkVector(128348, 2888, 59781)), # add the coordinates here (Get them using the console in game)
        Path.cwd() / 'example', # add the path where the base is stored
        Path.cwd() / 'example_modified_save'
    )