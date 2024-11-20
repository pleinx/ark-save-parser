from pathlib import Path
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.api.resource_api import ResourceApi
from arkparse.classes.resources import Resources

bp = Resources.Crafted.metal_ingot
string = "metal ingots"

save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)
api = ResourceApi(save)

stones = api.get_by_class([bp])

print(f"We farmed {api.get_count(stones)} {string}")

random_resource = stones.popitem()
print(f"First resource: {random_resource[1]}")
print(f"resource id1: {random_resource[1].net_id.id1}, resource id2: {random_resource[1].net_id.id2}")
print(f"hex id1 {hex(random_resource[1].net_id.id1)}, hex id2 {hex(random_resource[1].net_id.id2)}")
print(f"UUid {random_resource[0]}")
print(f"Hex UUID {hex(random_resource[0].int)}")