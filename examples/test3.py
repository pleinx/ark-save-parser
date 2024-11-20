from pathlib import Path
import os
from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.classes.dinos import Dinos


def main():
    path = os.path.join(os.getcwd(), "test_saves", "server.ark")
    save = AsaSave(Path(path))
    
    reader_config = GameObjectReaderConfiguration(
        blueprint_name_filter=lambda name: name == Dinos.Abberant.dodo
    )

    dodos = save.get_game_objects(reader_config)

    print(f"There are {len(dodos)} dodos on the map.")


if __name__ == "__main__":
    main()
