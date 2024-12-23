from arkparse import AsaSave
from pathlib import Path
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api import EquipmentApi
from arkparse import Classes
from arkparse.parsing import ArkBinaryParser
from uuid import UUID, uuid4
from arkparse.object_model.equipment import Weapon
from arkparse.logging import ArkSaveLogger
import random

# save_path = ArkFtpClient.from_config("../../ftp_config.json", FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save_path = Path.cwd() / "Aberration_WP.ark"
save = AsaSave(save_path, False)
eApi = EquipmentApi(save)

weapon_bps = eApi.get_filtered(EquipmentApi.Classes.WEAPON, only_blueprints=True)

random_bp: Weapon = random.choice(list(weapon_bps.values()))
ArkSaveLogger.enable_debug = True
ArkSaveLogger.set_file(random_bp.binary, "or_bp.bin")
ArkSaveLogger.open_hex_view()
random_bp.binary.find_names()
random_bp.object.print_properties()

prev_uuid = random_bp.object.uuid
new_uuid = uuid4()  
random_bp.reidentify(new_uuid, Classes.equipment.weapons.advanced.fabricated_sniper)
random_bp.set_damage(177.77)
random_bp.set_durability(377.77)
save.add_obj_to_db(new_uuid, random_bp.binary.byte_buffer)
random_bp.binary.find_names()
obj = save.get_game_object_by_id(new_uuid)

parser = ArkBinaryParser(save.get_game_obj_binary(new_uuid), save.save_context)
weapon = Weapon(new_uuid, parser)
print(f"New weapon: {weapon}")



