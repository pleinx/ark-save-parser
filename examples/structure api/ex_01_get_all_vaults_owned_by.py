from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave, Classes
from arkparse.api import StructureApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

structure_api = StructureApi(save)
owning_tribe = 0 # add the tribe id here (check the player api examples to see how to get the tribe id)

vaults: Dict[UUID, StructureWithInventory] = structure_api.get_by_class([Classes.structures.placed.utility.vault])
vaults_owned_by = [v for v in vaults.values() if v.owner.tribe_id == owning_tribe]

print(f"Vaults owned by tribe {owning_tribe}:")
for v in vaults_owned_by:
    print(v)
