from pathlib import Path
from arkparse.api.structure_api import StructureApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.structures.structure_with_inventory import StructureWithInventory
from arkparse.classes.placed_structures import PlacedStructures
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap


save_path = Path.cwd() / "test_saves" / "server.ark"
save_path = ArkFtpClient.from_config(Path("../ftp_config.json"), FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)
structure_api = StructureApi(save)
 
structures = structure_api.get_by_class(PlacedStructures.utility.large_storage_box)
print(f"Found {len(structures)} structures")

print("Structures:")
for key, structure in structures.items():
    structure: StructureWithInventory = structure
    print(f"Structure {key} has {len(structure.inventory.items)} items in its inventory {structure.inventory_uuid}:")
    for key, item in structure.inventory.items.items():
        print(f"Item {key} of type {item.object.blueprint}: ")
        print(item.object.print_properties())
        print("\n")


