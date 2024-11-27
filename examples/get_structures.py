from pathlib import Path
from arkparse.api.structure_api import StructureApi
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes.placed_structures import PlacedStructures


save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)
structure_api = StructureApi(save)
 
structures = structure_api.get_by_class(PlacedStructures.stone.floor)

print(f"Found {len(structures)} structures")

print("Structures:")
for key, structure in structures.items():
    print(structure.to_string_complete())
    print("\n")
