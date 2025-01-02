from pathlib import Path
import random
from uuid import UUID
from typing import Dict

from arkparse import AsaSave
from arkparse.api import BaseApi
from arkparse import Classes
from arkparse.object_model.bases.base import Base
from arkparse.logging import ArkSaveLogger
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkMap
from arkparse import MapCoords

save_path = Path.cwd() / "___Aberration_WP.ark"
# save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd())

turret = [Classes.structures.placed.turrets.auto]
bullet = [Classes.equipment.ammo.advanced_rifle_bullet]
save = AsaSave(save_path, False)
sApi = BaseApi(save, ArkMap.ABERRATION)

base: Base = sApi.get_base_at(MapCoords(45, 35.9))

base.pad_turret_ammo(10, save)

save.store_db(Path.cwd() / "Aberration_WP.ark")


