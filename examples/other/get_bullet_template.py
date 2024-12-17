from pathlib import Path
import random

from arkparse import AsaSave
from arkparse.api.stackable_api import StackableApi
from arkparse import Classes
from arkparse.logging import ArkSaveLogger
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.parsing import ArkBinaryParser

save_path = Path.cwd() / "Aberration_WP.ark"
# save_path = ArkFtpClient.from_config('../../ftp_config.json', FtpArkMap.ABERRATION).download_save_file(Path.cwd())

bullet = [Classes.equipment.ammo.advanced_rifle_bullet]
save = AsaSave(save_path)
sApi = StackableApi(save)

bullets = sApi.get_by_class(StackableApi.Classes.AMMO, bullet)

uuid = None
bullet = None

print(f"Found {len(bullets)} bullets")
for key, bullet in bullets.items():
    print(f"{key}: {bullet}")
    print(bullet.object.names)
    print(bullet.id_)

random_bullet_index = int(random.random() * len(bullets)) 

uuid = list(bullets.keys())[random_bullet_index]
bullet = bullets[uuid]

ArkSaveLogger.enable_debug = True
bin = save.get_game_obj_binary(uuid)
obj = save.get_game_object_by_id(uuid)
parser = ArkBinaryParser(bin, save.save_context)
parser.find_names()
ArkSaveLogger.open_hex_view(True)

bullet.replace_uuid()
bullet.id_.replace(bullet.binary)
bullet.set_quantity(100)

parser = ArkBinaryParser(bullet.binary.byte_buffer, save.save_context)
ArkSaveLogger.set_file(parser, "temp.bin")
ArkSaveLogger.open_hex_view(True)