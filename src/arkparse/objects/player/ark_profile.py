from pathlib import Path
from typing import List

from arkparse.parsing.ark_archive import ArkArchive

from .ark_player_data import ArkPlayerData
from .ark_persistent_buff_data import PersistentBuffData

class ArkProfile:
    """
    Reads Ark: Survival Ascended *.arkprofile files
    """

    _archive: ArkArchive
    player_data : ArkPlayerData
    persistent_buffs : List[PersistentBuffData]
    
    def __init__(self, file: Path):
        _archive = ArkArchive(file)
        
        self.player_data = ArkPlayerData(_archive.get_object_by_class("/Game/PrimalEarth/CoreBlueprints/PrimalPlayerDataBP.PrimalPlayerDataBP_C"))
        # print(self.player_data)

        self.persistent_buffs = []
        for buff in _archive.get_all_objects_by_class("/Script/ShooterGame.PrimalBuffPersistentData"):
            self.persistent_buffs.append(PersistentBuffData(buff))

        self._archive = _archive

    # def get_profile(self) -> Optional[ArkObject]:
    #     return self._archive.get_object_by_class("/Game/PrimalEarth/CoreBlueprints/PrimalPlayerDataBP.PrimalPlayerDataBP_C")
    
    # def get_persistent_buffs(self) -> List[PersistentBuffData]:
    #     buffs = []
    #     for buff in self._archive.get_all_objects_by_class("/Script/ShooterGame.PrimalBuffPersistentData"):
    #         buffs.append(PersistentBuffData(buff))
    #     return buffs
