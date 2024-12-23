from arkparse import AsaSave
from pathlib import Path
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api import EquipmentApi
from arkparse import Classes
from arkparse.parsing import ArkBinaryParser
from arkparse.api import StructureApi
from uuid import UUID, uuid4
from arkparse.object_model.equipment import Weapon, Saddle, Armor
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.logging import ArkSaveLogger
import random
from arkparse.enums import ArkItemQuality

# save_path = ArkFtpClient.from_config("../../ftp_config.json", FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save_path = Path.cwd() / "___Aberration_WP.ark"
save = AsaSave(save_path, False)
eApi = EquipmentApi(save)
sApi = StructureApi(save)

vaults = sApi.get_by_class(Classes.structures.placed.utility.vault)

v = None
for key, vault in vaults.items():
    if key == UUID("6645a506-4513-134b-a25f-624b75da7b7e"):
        v = vault


# WEAPON
cpb = None
for key, item in v.inventory.items.items():
    item : InventoryItem
    if item.object.blueprint == Classes.equipment.weapons.advanced.compound_bow:
        w: Weapon = Weapon.from_inventory_item(item, save)
        if w.is_bp:
            cpb = w
        break

if cpb is None:
    print("Compound bow not found")
    exit()

random_bp: Weapon = cpb
prev_uuid = random_bp.object.uuid
new_uuid = uuid4()  
random_bp.reidentify(new_uuid, Classes.equipment.weapons.advanced.fabricated_sniper)
random_bp.set_damage(177.77)
random_bp.set_durability(377.77)
random_bp.set_rating(8)
random_bp.set_quality_index(ArkItemQuality.ASCENDANT)
save.add_obj_to_db(new_uuid, random_bp.binary.byte_buffer)

random_bp.binary.find_names()
obj = save.get_game_object_by_id(new_uuid)
parser = ArkBinaryParser(save.get_game_obj_binary(new_uuid), save.save_context)
weapon = Weapon(new_uuid, parser)
print(f"New weapon: {weapon}")

vault.add_item(new_uuid)


# SADDLE
ss = None
for key, item in v.inventory.items.items():
    item : InventoryItem
    if item.object.blueprint == Classes.equipment.saddles.stego:
        w: Saddle = Saddle.from_inventory_item(item, save)
        if w.is_bp:
            ss = w
        break

if ss is None:
    print("Stego saddle not found")
    exit()

new_uuid = uuid4()
ss.reidentify(new_uuid, Classes.equipment.saddles.trike)
ss.set_quality_index(ArkItemQuality.MASTERCRAFT)
ss.set_armor(117.7)
ss.set_durability(217.7)
ss.set_rating(8)
save.add_obj_to_db(new_uuid, ss.binary.byte_buffer)
ss.binary.find_names()
obj = save.get_game_object_by_id(new_uuid)
parser = ArkBinaryParser(save.get_game_obj_binary(new_uuid), save.save_context)
saddle = Saddle(new_uuid, parser)
print(f"New saddle: {saddle}")

vault.add_item(new_uuid)

# ARMOR
aa = None
for key, item in v.inventory.items.items():
    item : InventoryItem
    if item.object.blueprint == Classes.equipment.armor.flak.shirt:
        w: Armor = Armor.from_inventory_item(item, save)
        if w.is_bp:
            aa = w
        break

if aa is None:
    print("Flak shirt not found")
    exit()

new_uuid = uuid4()
aa.reidentify(new_uuid, Classes.equipment.armor.hazard.gloves)
aa.set_quality_index(ArkItemQuality.JOURNEYMAN)
aa.set_armor(511.7)
aa.set_durability(611.7)
aa.set_rating(8)
save.add_obj_to_db(new_uuid, aa.binary.byte_buffer)
aa.binary.find_names()
obj = save.get_game_object_by_id(new_uuid)
parser = ArkBinaryParser(save.get_game_obj_binary(new_uuid), save.save_context)
armor = Armor(new_uuid, parser)
print(f"New armor: {armor}")

vault.add_item(new_uuid)

save.store_db(Path.cwd() / "Aberration_WP.ark")





