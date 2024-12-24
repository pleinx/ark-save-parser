from arkparse import AsaSave
from pathlib import Path
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api import EquipmentApi
from arkparse import Classes
from arkparse.enums import ArkItemQuality
from uuid import UUID
from arkparse.object_model.structures import StructureWithInventory
from arkparse.object_model.equipment import Saddle, Weapon, Armor, Shield

save_path = ArkFtpClient.from_config("../../ftp_config.json", FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)
eApi = EquipmentApi(save)

weapon_bps = eApi.get_filtered(EquipmentApi.Classes.ARMOR, only_blueprints=True, minimum_quality=ArkItemQuality.RAMSHACKLE)

rating_vs_sum_bp = []
rating_vs_sum = []

for key, value in weapon_bps.items():
    print(f"{key}: {value}")
    value: Saddle
    # value.object.print_properties()
    path = Path.cwd() / "templates" / "bp" / "armor" / value.get_short_name()
    path.mkdir(parents=True, exist_ok=True)
    value.store_binary(path)

    rating_vs_sum_bp.append([value.rating, value.get_average_stat(), value.quality])

weapons = eApi.get_filtered(EquipmentApi.Classes.ARMOR, no_bluepints=True, minimum_quality=ArkItemQuality.RAMSHACKLE)
for key, value in weapons.items():
    print(f"{key}: {value}")
    # value.object.print_properties()
    path = Path.cwd() / "templates" / "n_bp" / "armor" / value.get_short_name()
    path.mkdir(parents=True, exist_ok=True)
    value.store_binary(path)

    rating_vs_sum.append([value.rating, value.get_average_stat(), value.quality])

print(rating_vs_sum_bp)
print(rating_vs_sum)