from pathlib import Path
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.api.resource_api import ResourceApi
from arkparse.classes.resources import Resources

save_path = Path.cwd() / "test_saves" / "server.ark"
save = AsaSave(save_path)

value = b'\x00\x57\x1d\x2e'

save.find_value_in_game_table_objects(value)
save.find_value_in_custom_tables(value)