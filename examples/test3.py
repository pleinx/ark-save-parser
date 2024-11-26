from pathlib import Path
import os
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.api.dino_api import DinoApi
from arkparse.logging import ArkSaveLogger


def main():
    path = os.path.join(os.getcwd(), "test_saves", "server.ark")
    save = AsaSave(Path(path))

    # ArkSaveLogger.enable_debug = True
    # ArkSaveLogger.temp_file_path = Path.cwd()

    api: DinoApi = DinoApi(save)

    cryopodded = api.get_all_in_cryopod()

    print(f"Found {len(cryopodded)} cryopodded dinos")

    for dino in cryopodded.values():
        print(dino)

if __name__ == "__main__":
    main()
