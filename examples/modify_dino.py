from pathlib import Path
from uuid import UUID

from arkparse.enums import ArkStat
from arkparse.api.dino_api import DinoApi
from arkparse.objects.saves.game_objects.misc.dino_owner import DinoOwner
from arkparse.objects.saves.game_objects.dinos.tamed_dino import TamedDino

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.logging import ArkSaveLogger

ArkSaveLogger.temp_file_path = Path.cwd()

path = Path.cwd() / "Aberration_WP.ark"
save = AsaSave(path, read_only=False)
dino_api = DinoApi(save)

charles = dino_api.get_by_uuid(UUID("45c5eaee-f017-a24e-8448-f76b53bf1620"))

# Get Charles LeCrab
print(f"Found Charles LeCrab: {charles.get_short_name()}")
charles.object.print_properties()
print("\nHis stats:")
charles.stats.object.print_properties()

# Modify Charles LeCrab
charles.stats.modify_stat_value(ArkStat.HEALTH, 10000000000)
charles.stats.modify_stat_value(ArkStat.STAMINA, 10000000000)
charles.stats.modify_stat_value(ArkStat.WEIGHT, 10000000000)
charles.stats.modify_stat_value(ArkStat.FOOD, 10000000000)
charles.stats.modify_stat_value(ArkStat.WATER, 10000000000)
charles.stats.modify_stat_value(ArkStat.OXYGEN, 10000000000)
charles.stats.modify_stat_value(ArkStat.MELEE_DAMAGE, 0.1)
charles.stats.modify_stat_points(ArkStat.HEALTH, 0)
charles.stats.modify_stat_points(ArkStat.STAMINA, 0)
charles.stats.modify_stat_points(ArkStat.WEIGHT, 0)
charles.stats.modify_stat_points(ArkStat.FOOD, 0)
charles.stats.modify_stat_points(ArkStat.MELEE_DAMAGE, 0)
charles.stats.modify_experience(1000000000)
charles.stats.prevent_level_up()

admin_tribe_id = 1657686244
owner = DinoOwner()
owner.set_tribe("The Administribe", admin_tribe_id)
owner.player = "Mr Administrator"

charles: TamedDino = charles
charles.owner.replace_with(owner, charles.binary)

save.modify_game_obj(charles.object.uuid, charles.binary.byte_buffer)
save.modify_game_obj(charles.stats.object.uuid, charles.stats.binary.byte_buffer)

print("\nAfter modification:")
obj = save.get_game_object_by_id(charles.object.uuid)
obj.print_properties()

print("\nHis stats after modification:")
obj = save.get_game_object_by_id(charles.stats.object.uuid)
obj.print_properties()

# Store DB
save.store_db(Path.cwd() / "_Aberration_WP.ark")
