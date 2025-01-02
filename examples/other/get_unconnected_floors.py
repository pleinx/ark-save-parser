from pathlib import Path
from uuid import UUID

from arkparse import MapCoords
from arkparse.api.base_api import StructureApi
from arkparse.object_model.structures.structure import Structure
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.classes import *

# FTP = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION)
# SAVE = AsaSave(FTP.download_save_file(Path.cwd()))
SAVE = AsaSave(Path.cwd() / '___Aberration_WP.ark', False)

bApi = StructureApi(SAVE)

floors = bApi.get_by_class([Classes.structures.placed.tek.floor])
base_markers = []

for key, floor in floors.items():
    if len(floor.linked_structure_uuids) == 0:
        base_markers.append(floor)

for marker in base_markers:
    marker: Structure
    print("Found unconnected floor at", marker)
    print("Coordinates:", marker.location.as_map_coords(ArkMap.ABERRATION))
    print(marker.object.uuid)
    marker.heal()
    SAVE.modify_game_obj(marker.object.uuid, marker.binary.byte_buffer)

    marker.store_binary(Path.cwd() / "bases" / "base_marker" / "locations", True)

SAVE.store_db(Path.cwd() / "Aberration_WP.ark")