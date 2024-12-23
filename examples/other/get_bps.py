from arkparse import AsaSave
from pathlib import Path
from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api import EquipmentApi
from arkparse import Classes
from uuid import UUID
from arkparse.object_model.structures import StructureWithInventory

save_path = ArkFtpClient.from_config("../../ftp_config.json", FtpArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)
eApi = EquipmentApi(save)

weapon_bps = eApi.get_filtered(EquipmentApi.Classes.SADDLE, only_blueprints=True)

for key, value in weapon_bps.items():
    print(f"{key}: {value}")
    # value.object.print_properties()
    path = Path.cwd() / "bps" / "saddle" / value.get_short_name()
    path.mkdir(parents=True, exist_ok=True)
    value.store_binary(path)


