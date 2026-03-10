from pathlib import Path

from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration

print(Path.cwd())
save_path = Path.cwd() / "examples" / "asv_json_export" / "LC_FIX" / "LostColony_WP.ark"
save = AsaSave(save_path)

class_ = ["/Game/LostColony/CoreBlueprints/Patrols/NPCZoneManager_Patrols.NPCZoneManager_Patrols_C"]
config = GameObjectReaderConfiguration(blueprint_name_filter=lambda name: name is not None and any(cls in name for cls in class_))
objects = save.get_game_objects(config)

for key, obj in objects.items():
    save.remove_obj_from_db(obj.uuid)

print(f"Found and removed {len(objects)} objects with class {class_}")

save.store_db( Path.cwd() / "examples" / "asv_json_export" / "LC_FIX" / "LostColony_WP_fixed.ark")