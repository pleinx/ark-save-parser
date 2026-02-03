from pathlib import Path
from arkparse.parsing.ark_archive import ArkArchive
from arkparse.logging import ArkSaveLogger
from arkparse.parsing.ark_property_container import set_print_depth
from arkparse.player.ark_cluster_data import ClusterData

# ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ALL, True)

def get_files(path: Path) -> list[Path]:
    return [f for f in path.iterdir() if (f.is_file() and not f.name.endswith(".py"))]

files = get_files(Path().cwd())
for file in files:
    ArkSaveLogger.info_log(f"Found file: {file.name}")
    cluster_data = ClusterData(Path().cwd(), file.name)

# ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ALL, True)

# data = Path("./00027906d14846019887ee674cdcf0e1").read_bytes()
# data = Path("./00027906d14846019887ee674cdcf0e1_uploaded_dino2").read_bytes()
# data = Path("./00027906d14846019887ee674cdcf0e1_uploaded_dino").read_bytes()
# cluster_data = ArkArchive(data, from_store=False)
# set_print_depth(2)
# print(cluster_data)