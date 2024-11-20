from pathlib import Path

from arkparse.parsing.ark_archive import ArkArchive
from .ark_tribe_data import ArkTribeData

class ArkTribe:
    """
    Reads Ark: Survival Ascended *.arktribe files
    """
    _archive: ArkArchive
    tribe_data: ArkTribeData

    def __init__(self, file: Path):
        _archive = ArkArchive(file)

        tribe_props = _archive.get_object_by_class("/Script/ShooterGame.PrimalTribeData")
        if not tribe_props:
            raise ValueError("Failed to find tribe data.")
        else:
            self.tribe_data = ArkTribeData(tribe_props)

        self._archive = _archive

