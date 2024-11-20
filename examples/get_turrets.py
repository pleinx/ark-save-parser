from pathlib import Path
from arkparse.api.structure_api import StructureApi
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes.placed_structures import PlacedStructures


save_path = Path.cwd() / "Aberration_WP.ark"
save = AsaSave(save_path)
structure_api = StructureApi(save)
 
structures = structure_api.get_by_class(PlacedStructures.turrets.all_bps)

print(f"Found {structure_api.get_response_total_count(structures)} structures")

print("Structures:")
for key, structure in structures["structures"].items():
    print(structure.to_string_complete())

print("Structures with inventory:")
for key, structure in structures["structures_with_inventory"].items():
    print(structure.to_string_complete())

