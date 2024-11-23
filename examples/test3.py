from pathlib import Path
import os
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.api.player_api import PlayerApi, ArkMaps
from arkparse.logging import ArkSaveLogger


def main():
    path = os.path.join(os.getcwd(), "test_saves", "server.ark")
    save = AsaSave(Path(path))

    ArkSaveLogger.enable_debug = True
    ArkSaveLogger.temp_file_path = Path.cwd()

    pApi: PlayerApi = PlayerApi("../ftp_config.json", ArkMaps.ABERRATION, save=save)

    for player in pApi.players:
        print(f"Inventory of {player.player_data.name}:")
        for inv in player.inventory.values():
            print(f"Inventory: {inv.object.uuid}")
            for key, item in inv.items.items():
                bp = item.object.blueprint.split('.')[-1]
                print(f"  - Item ({key}): {bp}")


if __name__ == "__main__":
    main()
