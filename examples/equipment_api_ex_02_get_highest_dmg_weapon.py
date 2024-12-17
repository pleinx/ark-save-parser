from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.object_model.equipment.weapon import Weapon
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api.equipment_api import EquipmentApi

save_path = ArkFtpClient.from_config(Path("../ftp_config.json"), FtpArkMap.ABERRATION).download_save_file(Path.cwd()) # retrieve the save file (can also retrieve it from a local path)
save = AsaSave(save_path)

equipment_api = EquipmentApi(save) # Create Equipment API

weapons: Dict[UUID, Weapon] = equipment_api.get_filtered(EquipmentApi.Classes.WEAPON, no_bluepints=True)  # Get all weapons
highest_dmg_weapon = max(weapons.values(), key=lambda x: x.damage)                                        # Get weapon with highest damage

print(f"Highest damage on weapon: {highest_dmg_weapon.damage}")                                           # Print highest durability
print(f"Type: {highest_dmg_weapon.get_short_name()}")                                                     # Print type of weapon with highest damage   
if highest_dmg_weapon.crafter:
    print(f"Crafted by: {highest_dmg_weapon.crafter}")                                                    # Print crafter of weapon with highest damage
else:
    print("Not crafted (found as loot or spawned in)")                                                    # Print if weapon with highest damage is not crafted