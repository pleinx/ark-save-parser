from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave
from arkparse.api import StructureApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.RAGNAROK).download_save_file(Path.cwd())
save = AsaSave(save_path)

structure_api = StructureApi(save)
structures: Dict[UUID, StructureWithInventory] = structure_api.get_all()

for struct_uuid, structure in structures.items():
    print(structure.owner)