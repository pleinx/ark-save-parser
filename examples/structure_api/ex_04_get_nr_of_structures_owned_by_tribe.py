from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave
from arkparse.api import StructureApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.structures import Structure

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

owner_tribe_id = 0 # add the tribe id here (check the player api examples to see how to get the tribe id)
structure_api = StructureApi(save)
all_structures: Dict[UUID, Structure] = structure_api.get_owned_by(owner_tribe_id = owner_tribe_id)

print(f"Number of structures owned by tribe {owner_tribe_id}: {len(all_structures)}")