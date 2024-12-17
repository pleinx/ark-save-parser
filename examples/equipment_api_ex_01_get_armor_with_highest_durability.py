from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.object_model.equipment.armor import Armor
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api.equipment_api import EquipmentApi

save_path = ArkFtpClient.from_config(Path("../ftp_config.json"), FtpArkMap.ABERRATION).download_save_file(Path.cwd()) # retrieve the save file (can also retrieve it from a local path)
save = AsaSave(save_path)

equipment_api = EquipmentApi(save) # Create Equipment API

armor: Dict[UUID, Armor] = equipment_api.get_all(EquipmentApi.Classes.ARMOR, no_bluepints=True)    # Get all armor
armor_with_highest_durability = max(armor.values(), key=lambda x: x.durability)                    # Get armor with highest durability

print(f"Highest durability armor: {armor_with_highest_durability.durability}")                     # Print highest durability
print(f"Type: {armor_with_highest_durability.get_short_name()}")                                   # Print type of armor with highest durability   
if armor_with_highest_durability.crafter:
    print(f"Crafted by: {armor_with_highest_durability.crafter}")                                  # Print crafter of armor with highest durability
else:
    print("Not crafted (found as loot or spawned in)")                                             # Print if armor with highest durability is not crafted