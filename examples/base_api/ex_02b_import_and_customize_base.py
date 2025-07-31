from pathlib import Path

from arkparse import AsaSave, Classes
from arkparse.parsing.struct.actor_transform import ActorTransform, ArkVector
from arkparse.enums import ArkMap, ArkEquipmentStat
from arkparse.api import BaseApi, EquipmentApi
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.object_model.bases.base import Base
from arkparse.object_model.structures import StructureWithInventory

def add_stuff_to_vault(save: AsaSave, base: Base, is_bp: bool = False):
    e_api = EquipmentApi(save)

    # Get a vault from the base
    vault: StructureWithInventory = None
    for _, structure in base.structures.items():
        if structure.object.blueprint == Classes.structures.placed.utility.vault:
            vault = structure

    # Add an armor bp to the vault
    min_armor = 400
    max_armor = 800
    item = e_api.generate_equipment(
        EquipmentApi.Classes.ARMOR, Classes.equipment.armor.flak.helmet, ArkEquipmentStat.ARMOR, min_armor, max_armor, force_bp=is_bp)
    save.add_to_db(item)
    vault.add_item(item.object.uuid, save)

def ex_02b_import_and_customize_base(save_path: Path, modified_save_path: Path, base_file_path: Path, map: ArkMap, import_at: ActorTransform):
    """
    Example to import a base from a save file and customize it.
    :param is_bp: If True, the items will be added as blueprints, otherwise as items.
    """
    if not Path.cwd().exists():
        raise FileNotFoundError(f"Current working directory does not exist at {Path.cwd()}")

    SAVE = AsaSave(save_path)
    b_api = BaseApi(SAVE, map)
    

    base: Base = b_api.import_base(base_file_path, import_at)
     
    # Optional: you can add things to a vault in the base or simlilar structure like this:
    # add_stuff_to_vault(SAVE, base, is_bp=True)

    # Pad all turrets to 25 stacks of arb (or until turrets are full)
    nr_of_stacks = 25
    base.pad_turret_ammo(nr_of_stacks, SAVE)

    # Add 10 element to all tek generators
    nr_of_fuel = 10
    base.set_nr_of_fuel_in_generators(nr_of_fuel, SAVE)

    # Store the save
    SAVE.store_db(modified_save_path)

if __name__ == '__main__':
    # retrieve the save file (can also retrieve it from a local path)
    map_ = ArkMap.ABERRATION
    path = ArkFtpClient.from_config('../ftp_config.json', map_).download_save_file(Path.cwd())
    import_location = ActorTransform(ArkVector(128348, 2888, 59781)) # add the coordinates here (Get them using the console in game)
    base_storage_path = Path.cwd() / 'example' # add the path where the base is stored
    save_storage_path = Path.cwd() / 'example_modified_save' # add the path where the save is stored
    ex_02b_import_and_customize_base(path, save_storage_path, base_storage_path, map_, import_location)
