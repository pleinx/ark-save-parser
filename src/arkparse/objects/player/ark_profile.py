from pathlib import Path
from typing import List, Dict
from uuid import UUID

from arkparse.objects.saves.asa_save import AsaSave
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.objects.saves.game_objects.abstract_game_object import AbstractGameObject
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.parsing.ark_archive import ArkArchive
from arkparse.struct.actor_transform import ActorTransform
from arkparse.objects.saves.game_objects.misc.inventory import Inventory
from arkparse.classes.player import Player

from .ark_player_data import ArkPlayerData
from .ark_persistent_buff_data import PersistentBuffData

class ArkProfile:
    """
    Reads Ark: Survival Ascended *.arkprofile files
    """

    _archive: ArkArchive
    player_data : ArkPlayerData
    persistent_buffs : List[PersistentBuffData]
    location: ActorTransform
    inventory: Dict[UUID, Inventory]
    
    def __init__(self, file: Path):
        _archive = ArkArchive(file)
        
        self.player_data = ArkPlayerData(_archive.get_object_by_class("/Game/PrimalEarth/CoreBlueprints/PrimalPlayerDataBP.PrimalPlayerDataBP_C"))
        # print(self.player_data)

        self.persistent_buffs = []
        for buff in _archive.get_all_objects_by_class("/Script/ShooterGame.PrimalBuffPersistentData"):
            self.persistent_buffs.append(PersistentBuffData(buff))

        self._archive = _archive
        self.inventory = {}

    def get_location_and_inventory(self, save: AsaSave, pawns: Dict[UUID, AbstractGameObject] = None):
        if pawns is None:
            pawn_bps = [Player.pawn_female, Player.pawn_male]

            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and name in pawn_bps,
            )

            pawns = save.get_game_objects(config)

        # Look for the pawn that matches the player data
        for key, pawn in pawns.items():
            if pawn.get_property_value("LinkedPlayerDataID") == self.player_data.id_:
                self.location = ActorTransform(vector = pawn.get_property_value("SavedBaseWorldLocation"))
                inv_uuid = UUID(pawn.get_property_value("MyInventoryComponent").value)
                reader = ArkBinaryParser(save.get_game_obj_binary(inv_uuid), save.save_context)
                self.inventory = {inv_uuid: Inventory(inv_uuid, reader, container_type="Player inventory", save=save)}