from pathlib import Path

from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api.player_api import PlayerApi
from arkparse.api.equipment_api import EquipmentApi
from arkparse.api.structure_api import StructureApi
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.classes import *

# FTP = ArkFtpClient.from_config('../../ftp_config.json', FtpArkMap.ABERRATION)
# SAVE = AsaSave(FTP.download_save_file(Path.cwd()))
SAVE = AsaSave(Path.cwd() / 'Aberration_WP.ark')

# player_api = PlayerApi('../../ftp_config.json', FtpArkMap.ABERRATION, save=SAVE)
equipment_api = EquipmentApi(SAVE)
structure_api = StructureApi(SAVE)

clsses = Classes.equipment.armor.flak.all_bps
targets = equipment_api.get_by_class(EquipmentApi.Classes.ARMOR, classes=clsses)

for key, target in targets.items():
    if target.is_bp:
        print(target)
        inv_uuid = target.get_inventory(SAVE).object.uuid
        container = structure_api.get_container_of_inventory(inv_uuid)
        if container is not None:
            print(container.owner)
