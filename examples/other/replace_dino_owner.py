from pathlib import Path
import json

from arkparse.api.structure_api import ArkMap, MapCoords
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.api.player_api import PlayerApi
from arkparse.api.dino_api import DinoApi

from arkparse.saves.asa_save import AsaSave
from arkparse.logging import ArkSaveLogger

ArkSaveLogger.temp_file_path = Path.cwd()

path = Path.cwd() / "test_saves"
ftp = Path.cwd().parent / "ftp_config.json"

client = ArkFtpClient.from_config(ftp, FtpArkMap.ABERRATION)
client.connect()
client.download_save_file(path)
client.close()

save = AsaSave(path / "Aberration_WP.ark", read_only=False)
dino_api = DinoApi(save)
player_api = PlayerApi(ftp_config=ftp, map=FtpArkMap.ABERRATION, save=save)
dinos = dino_api.get_at_location(ArkMap.ABERRATION, MapCoords(20.6, 29.3), 0.3, tamed=True, untamed=False)

print(f"Found {len(dinos)} dinos\n")
new_owner = player_api.get_as_owner(347473876, PlayerApi.OwnerType.DINO)

if dinos is not None:
    print("Replacing owner to 'Human':")
    dino_api.modify_dinos(dinos, new_owner=new_owner, ftp_client=client)
    print("Done")

    print("\nReparsing binary")
    for key, dino in dinos.items():
        print("\n")
        dino : TamedDino = dino
        new_dino = TamedDino(key, dino.binary, save)
        dino.object.print_properties()
    print("Done")