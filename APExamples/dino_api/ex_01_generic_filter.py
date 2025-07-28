import json
from uuid import UUID
from typing import Dict
from pathlib import Path

from arkparse.enums import ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import TamedDino, Dino
from arkparse.logging import ArkSaveLogger


def ex_01_generic_filter(save_path: Path, lower_lvl: int = None, upper_lvl: int = None,
                       classes: list[str] = None, tamed: bool = None,
                       stat_point_requirement: int = None, stats: list[str] = None) -> None:
    """
    Get filtered dinos from the save file.
    """
    save = AsaSave(save_path)                  # load the save file
    dApi = DinoApi(save)                       # create a DinoApi object

    dinos: Dict[UUID, Dino] = dApi.get_all_filtered(level_lower_bound=lower_lvl,
                                level_upper_bound=upper_lvl,
                                class_names=classes,
                                tamed=tamed,
                                stat_minimum=stat_point_requirement,
                                stats=stats,
                                only_cryopodded=True)

    ArkSaveLogger.info_log("Dinos:") # print filter configuration
    if classes is not None:
        ArkSaveLogger.info_log(f"   - Class = {classes}")
    if lower_lvl is not None:
        ArkSaveLogger.info_log(f"   - Lower level = {lower_lvl}")
    if upper_lvl is not None:
        ArkSaveLogger.info_log(f"   - Upper level = {upper_lvl}")
    if tamed is not None:
        ArkSaveLogger.info_log(f"   - Tamed = {tamed}")
    if stat_point_requirement is not None:
        ArkSaveLogger.info_log(f"   - Stat point requirement = {stat_point_requirement}")
        if stats is not None:
            ArkSaveLogger.info_log(f"   - Stats = {stats}")

    level_distribution: Dict[int, int] = dApi.count_by_level(dinos)
    class_distribution: Dict[str, int] = dApi.count_by_class(dinos)

    return dinos, level_distribution, class_distribution

if __name__ == "__main__":
    # if configured to None, the filter will not be applied
    classes = None                   # replace with the classes of the dinos you want to filter for ex. [Dinos.basilisk, Dinos.reaper_queen]
    lower_lvl = None                # replace with the lower level bound ex. 100
    upper_lvl = None                # replace with the upper level bound ex. 150
    tamed = True                    # replace with True or False to filter for tamed or wild dinos
    stat_point_requirement = None   # replace with the minimum number of points in a single stat required ex. 40
    stats = None                    # replace with the stats you want to apply stat_point_requirement for ex. [ArkStat.HEALTH, ArkStat.MELEE_DAMAGE], None means all stats

    save_path = Path.cwd() / "save.ark" # replace with path to your save file

    dinos, level_distribution, class_distribution = ex_01_generic_filter(
        save_path,
        lower_lvl,
        upper_lvl,
        classes,
        tamed,
        stat_point_requirement,
        stats
    )

    # print the number of dinos per level
    print("\nBy level:")
    print(json.dumps(level_distribution, indent=4))

    # print the number of dinos per class
    print("\nBy class:")
    print(json.dumps(class_distribution, indent=4))

    # print the locations of the filtered dinos
    print("\n")
    nr_prnted = 0
    dinos: dict
    for key, dino in dinos.items():
        dino: Dino # type hint
        if isinstance(dino, TamedDino) and dino.cryopod is not None:
            print(f"{key}: location = Cryopod {dino.get_short_name()} (lv {dino.stats.current_level})")
        else:
            print(f"{key}: location = {dino.location.as_map_coords(ArkMap.ABERRATION)}")

        nr_prnted += 1
        if nr_prnted >= 10:  # limit the output to 10 dinos
            print("... and more")
            break

