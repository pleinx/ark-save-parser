from pathlib import Path
import random
from uuid import UUID
from typing import Dict

from arkparse import AsaSave
from arkparse.api.stackable_api import StackableApi
from arkparse.api.structure_api import StructureApi
from arkparse import Classes
from arkparse.object_model.stackables import Ammo
from arkparse.object_model.structures import StructureWithInventory
from arkparse.logging import ArkSaveLogger
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkMap
from arkparse import MapCoords

save_path = Path.cwd() / "___Aberration_WP.ark"
# save_path = ArkFtpClient.from_config('../../ftp_config.json', FtpArkMap.ABERRATION).download_save_file(Path.cwd())

turret = [Classes.structures.placed.turrets.auto]
bullet = [Classes.equipment.ammo.advanced_rifle_bullet]
save = AsaSave(save_path, False)
sApi = StackableApi(save)
stApi = StructureApi(save)

bullets = sApi.get_by_class(StackableApi.Classes.AMMO, bullet)

uuid = None
bullet = None

print(f"Found {len(bullets)} bullets")
# for key, bullet in bullets.items():
#     print(f"{key}: {bullet}")
#     print(bullet.object.names)
#     print(bullet.id_)

random_bullet_index = int(random.random() * len(bullets)) 

uuid = list(bullets.keys())[random_bullet_index]
bullet = bullets[uuid]

turrets: Dict[UUID, StructureWithInventory] = stApi.get_by_class(turret)

for key, turret in turrets.items():
    print(turret.object.blueprint)

def new_bullet(template: Ammo):
    template.replace_uuid()
    template.id_.replace(template.binary)
    template.set_quantity(100)

    random_bytes = bytes([random.randint(49, 57) for _ in range(10)])
    template.binary.replace_bytes(random_bytes, position=57)

    # ArkSaveLogger.set_file(bullet.binary, "temp.bin")
    # ArkSaveLogger.open_hex_view(True)

    # print("New bullet:")
    # print(f"{template.object.uuid}: {template}")
    # print(template.object.names)
    # print(template.id_)

    return template

# ArkSaveLogger.enable_debug = True
# ArkSaveLogger.set_file(bullet.binary, "temp.bin")
# ArkSaveLogger.open_hex_view(True)

save.print_tables_and_sizes()
print(f"Found {len(turrets)} turrets")
for key, turret in turrets.items():
    while len(turret.inventory.items) < 10:
        new = new_bullet(bullet)
        print(f"Adding bullet ({new.object.uuid}) to {key}")
        save.add_obj_to_db(new.object.uuid, new.binary.byte_buffer)
        turret.add_item(new.object.uuid)

save.print_tables_and_sizes()
save.store_db(Path.cwd() / "Aberration_WP.ark")

