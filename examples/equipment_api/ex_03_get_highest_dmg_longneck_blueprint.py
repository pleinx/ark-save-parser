from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.object_model.equipment.weapon import Weapon
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.equipment_api import EquipmentApi
from arkparse.classes.equipment import Weapons

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

equipment_api = EquipmentApi(save)  # Create Equipment API

weapons: Dict[UUID, Weapon] = equipment_api.get_filtered(EquipmentApi.Classes.WEAPON,          # Get all longneck bps
                                                         classes=[Weapons.advanced.longneck],
                                                         only_blueprints=True)
highest_dmg_bp = max(weapons.values(), key=lambda x: x.damage)                                 # Get longneck bp with highest damage
print(f"Highest damage on longneck bp: {highest_dmg_bp.damage}")
