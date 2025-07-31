from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.object_model.equipment.weapon import Weapon
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api import EquipmentApi, StructureApi
from arkparse.classes.equipment import Weapons
from arkparse.object_model.structures.structure_with_inventory import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

equipment_api = EquipmentApi(save)  # Create Equipment API
structure_api = StructureApi(save)

for w in Weapons.advanced.all_bps:
    weapons: Dict[UUID, Weapon] = equipment_api.get_filtered(EquipmentApi.Classes.WEAPON,
                                                            classes=[w],
                                                            only_blueprints=True)
    
    if len(weapons) > 0:
        highest_dmg_bp = max(weapons.values(), key=lambda x: x.damage)
        print(f"Highest damage on {highest_dmg_bp.get_short_name()} bp: {highest_dmg_bp.damage}")

        for key, value in weapons.items():
            container: StructureWithInventory = structure_api.get_container_of_inventory(value.owner_inv_uuid)
            if container is None:
                print(value)
                print(f"Owner of {value.get_short_name()} bp is not found. Owner inv was {value.owner_inv_uuid}\n")
                continue
            
            print(value)
            print(f"Owner is: {container.owner}\n")

