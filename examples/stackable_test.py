from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.objects.saves.game_objects.misc.inventory_item import InventoryItem
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.api.stackable_api import StackableApi
from arkparse.classes import Classes

bp = Classes.equipment.weapons.ammo.arrow_stone
string = "ammo items"
cls = StackableApi.Classes.AMMO

save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)
api = StackableApi(save)

items: Dict[UUID, InventoryItem] = api.get_by_class(cls, [bp])

print(f"We farmed {api.get_count(items)} {string}")

for key, item in items.items():
    item.object.print_properties()