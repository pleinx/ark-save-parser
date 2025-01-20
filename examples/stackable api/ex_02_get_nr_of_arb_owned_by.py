from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave, Classes
from arkparse.api import StackableApi, StructureApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.stackables import Ammo
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

map = ArkMap.ABERRATION
api = StackableApi(save)

arb = Classes.equipment.ammo.advanced_rifle_bullet
owner_tribe_id = 1173560527 # add the tribe id here (check the player api examples to see how to get the tribe id)

# Get all advanced rifle bullets
print("Retrieving all advanced rifle bullets...")
stacks: Dict[UUID, Ammo] = api.get_by_class(StackableApi.Classes.AMMO, arb)

structure_api = StructureApi(save)
owned_by: Dict[UUID, int] = {}

# filter by tribe id
print("Filtering by tribe id by retrieving containers...")
found_containers = {}
for key, stack in stacks.items():
    if stack.owner_inv_uuid not in found_containers:
        container: StructureWithInventory = structure_api.get_container_of_inventory(stack.owner_inv_uuid)
        found_containers[stack.owner_inv_uuid] = container
    else:
        container = found_containers[stack.owner_inv_uuid]

    if container is not None and container.owner.tribe_id == owner_tribe_id:
        owned_by[key] = stack

total = api.get_count(owned_by)

print(f"Total number of advanced rifle bullets owned by tribe {owner_tribe_id}: {total}")
