from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave, Classes
from arkparse.api import StackableApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.stackables import Resource

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

map = ArkMap.ABERRATION
api = StackableApi(save)

# example resource: electronics
resource = Classes.resources.Crafted.electronics
short_name = resource.split(".")[-1]

resource_stacks: Dict[UUID, Resource] = api.get_by_class(StackableApi.Classes.RESOURCE, resource)
total = api.get_count(resource_stacks)

print(f"Total number of {short_name} in the save: {total}")
