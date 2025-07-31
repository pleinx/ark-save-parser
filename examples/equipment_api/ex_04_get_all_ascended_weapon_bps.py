from pathlib import Path
from uuid import UUID
from typing import Dict


from arkparse import AsaSave
from arkparse.enums import ArkMap, ArkItemQuality
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.api.equipment_api import EquipmentApi
from arkparse.classes.equipment import Weapons
from arkparse.object_model.equipment.weapon import Weapon

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

equipment_api = EquipmentApi(save)  # Create Equipment API

weapons: Dict[UUID, Weapon] = equipment_api.get_filtered(EquipmentApi.Classes.WEAPON,              # Get all longneck bps,
                                                         minimum_quality=ArkItemQuality.ASCENDANT, # only ascendant quality
                                                         only_blueprints=True)

for key, weapon in weapons.items():
    print(weapon)
