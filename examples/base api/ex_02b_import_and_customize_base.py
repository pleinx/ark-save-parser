from pathlib import Path

from arkparse import AsaSave, Classes
from arkparse.parsing.struct.actor_transform import ActorTransform, ArkVector
from arkparse.enums import ArkMap, ArkEquipmentStat
from arkparse.api import BaseApi, EquipmentApi
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.object_model.bases.base import Base
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
map_ = ArkMap.ABERRATION
path = ArkFtpClient.from_config('../ftp_config.json', map_).download_save_file(Path.cwd())
import_location = ActorTransform(ArkVector(128348, 2888, 59781)) # add the coordinates here (Get them using the console in game)
size = 1 # add the size here (in map coordinates)
base_storage_path = Path.cwd() / 'example' # add the path where the base is stored
save_storage_path = Path.cwd() / 'example_modified_save' # add the path where the save is stored

SAVE = AsaSave(path)
b_api = BaseApi(SAVE, map_)
e_api = EquipmentApi(SAVE)

base: Base = b_api.import_base(base_storage_path, import_location)

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
SAVE.add_to_db(item)
vault.add_item(item.object.uuid, SAVE)

# Pad all turrets to 25 stacks of arb
nr_of_stacks = 25
base.pad_turret_ammo(nr_of_stacks, SAVE)

# Add 10 element to all tek generators
nr_of_element = 10
base.set_nr_of_element_in_generators(nr_of_element, SAVE)

# Store the save
SAVE.store_db(save_storage_path)