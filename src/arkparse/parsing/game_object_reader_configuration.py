from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from arkparse.objects.saves.game_objects.ark_game_object import ArkGameObject
from .game_object_parser_configuration import GameObjectParserConfiguration


@dataclass
class GameObjectReaderConfiguration(GameObjectParserConfiguration):
    uuid_filter: Optional[Callable[[UUID], bool]] = None
    blueprint_name_filter: Optional[Callable[[Optional[str]], bool]] = None
    game_object_filter: Optional[Callable[['ArkGameObject'], bool]] = None

    binary_files_output_directory: Optional[Path] = None
    json_files_output_directory: Optional[Path] = None
