from pathlib import Path

from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing.ark_archive import ArkArchive

class ClusterData:
    def __init__(self, path: Path, uuid: str):
        self._path = path
        self._uuid = uuid
        self._archive_object: ArkArchive = self._parse()
        self._ark_data = self._archive_object.get_object_by_class("/Script/ShooterGame.ArkCloudInventoryData")
        self._ark_data_items: list[ArkGameObject] = self._ark_data.get_property_value("ArkItems", [])

        for item in self._ark_data_items:
            print(item.get_property_value("ItemArchetype").value)

    def _check_exists(self):
        path_exists = self._path.exists()

        if not path_exists:
            raise FileNotFoundError(f"Cluster data folder not found at path: {self._path}")

        file_path = self._path / f"{self._uuid}"
        file_exists = file_path.exists()

        if not file_exists:
            raise FileNotFoundError(f"Cluster data file not found in folder: {file_path}")
        
    def _parse(self) -> ArkArchive:
        self._check_exists()

        file_path = self._path / f"{self._uuid}"
        with open(file_path, "rb") as f:
            data = f.read()

        return ArkArchive(data, from_store=False)

    