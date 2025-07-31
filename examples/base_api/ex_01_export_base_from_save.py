from pathlib import Path

from arkparse import AsaSave, MapCoords
from arkparse.enums import ArkMap
from arkparse.api import BaseApi
from arkparse.ftp.ark_ftp_client import ArkFtpClient

# retrieve the save file (can also retrieve it from a local path)
def ex_01_export_base_from_save(path: Path, location: MapCoords, map: ArkMap):
    """
    Example to export a base from a save file.
    :param path: Path to the save file
    """
    if not path.exists():
        raise FileNotFoundError(f"Save file does not exist at {path}")
    location = MapCoords(80, 75.5) # add the coordinates here
    SAVE = AsaSave(path)
    bApi = BaseApi(SAVE, ArkMap.ABERRATION)
    # the radius is the radius around the location where the base should be searched
    base = bApi.get_base_at(location, radius=1)
    base.store_binary(storage_path)


if __name__ == '__main__':
    path = ArkFtpClient.from_config('../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd())
    storage_path = Path.cwd() / 'example_base_export' # add the path where the base should be stored

    ex_01_export_base_from_save(path, MapCoords(80, 75.5), ArkMap.ABERRATION)
