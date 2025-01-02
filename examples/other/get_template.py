from pathlib import Path
import random
from uuid import UUID

from arkparse import AsaSave
from arkparse.api.structure_api import StructureApi
from arkparse import Classes
from arkparse.logging import ArkSaveLogger
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.parsing import ArkBinaryParser

# save_path = Path.cwd() / "Aberration_WP.ark"
save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd())

turret = [Classes.structures.placed.turrets.auto]
save = AsaSave(save_path)
sApi = StructureApi(save)

turrets = sApi.get_by_class(turret)

print(f"Found {len(turrets)} turrets")
for key, turret in turrets.items():
    print(f"{key}: {turret}")
    print(turret.object.names)
    print(turret.id_)

# filter with inventory

random_index = int(random.random() * len(turrets)) 

uuid = list(turrets.keys())[random_index]
turr = turrets[uuid]

ArkSaveLogger.enable_debug = True
bin = save.get_game_obj_binary(uuid)
obj = save.get_game_object_by_id(uuid)
parser = ArkBinaryParser(bin, save.save_context)
parser.find_names()

obj = save.get_game_object_by_id(UUID("ce6b21a5-0e59-4c4d-8b72-0fe2df1f3690"))
obj = save.get_game_object_by_id(UUID("b999f87f-c2b2-b844-8e18-f01a2c593245"))
obj = save.get_game_object_by_id(UUID("15f103f1-c668-6949-8edf-25d18582d577"))
obj = save.get_game_object_by_id(UUID("6173debc-131a-2b48-882c-d043dac9be8e"))
obj = save.get_game_object_by_id(UUID("eae12b2e-e4b1-8547-8686-ba3e74ae1569"))