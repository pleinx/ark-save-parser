from pathlib import Path
import json

from arkparse.api.structure_api import StructureApi, ArkMap, MapCoords
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.object_model.structures.structure import Structure
from arkparse.api.player_api import PlayerApi



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
structure_api = StructureApi(save)
player_api = PlayerApi(ftp_config=ftp, map=FtpArkMap.ABERRATION, save=save)

structures = structure_api.get_at_location(ArkMap.ABERRATION, MapCoords(20.6, 29.3), 0.3)
print(f"Found {len(structures)} structures\n")


new_owner = player_api.get_as_owner(347473876, PlayerApi.OwnerType.OBJECT)

all_structures = structure_api.get_connected_structures(structures)
print("Connected building structure count: ", len(all_structures))

# for key, structure in all_structures.items():
#     print("\n")
#     structure.object.print_properties()

if all_structures is not None:
    print("Replacing owner to 'Human':")
    structure_api.modify_structures(all_structures, new_owner=new_owner, new_max_health=100000.0)
    print("Done")

    print("\nReparsing binary")
    for key, structure in all_structures.items():
        structure : Structure = structure
        new_structure = Structure(key, structure.binary)
        print(structure.to_string_complete())
        print("\n")
    print("Done")

    save.store_db(Path.cwd() / "Aberration_WP.ark")
    client.connect()
    client.upload_save_file(path=Path.cwd() / "Aberration_WP.ark")
    client.close()