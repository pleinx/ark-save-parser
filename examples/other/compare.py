from pathlib import Path
from arkparse import AsaSave
from uuid import UUID

from arkparse.parsing import ArkBinaryParser
from arkparse.logging import ArkSaveLogger
from arkparse.object_model import ArkGameObject

ArkSaveLogger.enable_debug = True
path1 = Path.cwd() / "bases" / "turret_tower" / "temp" / "str_0b219354-ff7c-41fd-b54b-3c83cd479ac2.bin"
path2 = Path.cwd() / "bases" / "turret_tower" / "temp2" / "str_0b219354-ff7c-41fd-b54b-3c83cd479ac2.bin"


save1 = AsaSave(Path.cwd() / 'Aberration_WP.ark')
save2 = AsaSave(Path.cwd() / '__Aberration_WP.ark')

bytes1 = path1.read_bytes()
bytes2 = path2.read_bytes()

p1 = ArkBinaryParser(bytes1, save1.save_context)
p1.find_names()
p2 = ArkBinaryParser(bytes2, save2.save_context)
p2.find_names()

o1 = ArkGameObject(UUID("0b219354-ff7c-41fd-b54b-3c83cd479ac2"), binary_reader=p1)
o2 = ArkGameObject(UUID("0b219354-ff7c-41fd-b54b-3c83cd479ac2"), binary_reader=p2)