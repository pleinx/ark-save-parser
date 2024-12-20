from arkparse import AsaSave
from pathlib import Path
import random
from uuid import UUID
from typing import Dict

from arkparse.api import BaseApi
from arkparse.enums import ArkMap

save_path = Path.cwd() / "_Aberration_WP.ark"
base_path = Path.cwd() / "test_base"
save = AsaSave(save_path, False)

bApi = BaseApi(save, ArkMap.ABERRATION)

structures = bApi.import_base(base_path)

save.store_db(Path.cwd() / "with_import.ark")
