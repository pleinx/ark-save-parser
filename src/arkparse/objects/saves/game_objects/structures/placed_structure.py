from dataclasses import dataclass
from typing import List
from uuid import UUID

from arkparse.objects.saves.game_objects.misc.__parsed_object_base import ParsedObjectBase
from arkparse.objects.saves.game_objects.misc.object_owner import ObjectOwner
from arkparse.struct.object_reference import ObjectReference
from arkparse.parsing import ArkPropertyContainer
from arkparse.struct import ActorTransform
from arkparse.parsing import ArkBinaryParser

@dataclass
class SimpleStructure(ParsedObjectBase):
    owner: ObjectOwner
    id_: int #StructureID
    max_health: float#MaxHealth
    current_health: float#Health

    location: ActorTransform
    binary_data: bytes

    linked_structure_uuids: List[str]#LinkedStructures
    linked_structures = List["SimpleStructure"]

    # timestamps
    original_creation_time: float #OriginalCreationTime
    last_enter_stasis_time: float #LastEnterStasisTime
    has_reset_decay_time: bool #bHasResetDecayTime
    saved_when_stasised: bool #bSavedWhenStasised

    # other
    was_placement_snapped: bool #bWasPlacementSnapped
    last_in_ally_range_time_serialized: float #LastInAllyRangeTimeSerialized

    #?
    #StructuresPlacedOnFloor
    #PrimarySnappedStructureChild
    #BedID
    #NextAllowedUseTime
    #PlacedOnFloorStructure
    #LinkedPlayerID
    #LinkedPlayerName
    #bInitializedRotation
    #DoorOpenState
    #CurrentOpenMode
    #CurrentItemCount
    #MyInventoryComponent
    #NetDestructionTime

    def __init__(self, uuid: UUID, binary: ArkBinaryParser):
        super().__init__(uuid, binary)

        properties = self.object
        self.owner = ObjectOwner(properties)

        self.id_ = properties.get_property_value("StructureID")
        self.max_health = properties.get_property_value("MaxHealth")
        self.current_health = properties.get_property_value("Health", self.max_health)

        self.location = None
        self.binary_data = None

        linked: List[ObjectReference] = properties.get_array_property_value("LinkedStructures", [])
        self.linked_structure_uuids = [UUID(link.value) for link in linked]
        self.linked_structures = []

        self.original_creation_time = properties.get_property_value("OriginalCreationTime")
        self.last_enter_stasis_time = properties.get_property_value("LastEnterStasisTime")
        self.has_reset_decay_time = properties.get_property_value("bHasResetDecayTime", False)
        self.saved_when_stasised = properties.get_property_value("bSavedWhenStasised", False)

        self.was_placement_snapped = properties.get_property_value("bWasPlacementSnapped", False)
        self.last_in_ally_range_time_serialized = properties.get_property_value("LastInAllyRangeTimeSerialized")

    def set_actor_transform(self, actor_transform: ActorTransform):
        self.location = actor_transform

    def set_binary_data(self, binary_data: bytes):
        self.binary_data = binary_data

    def overwrite_health(self, health: float):
        self.max_health = health
        self.binary.replace_float(self.binary.set_property_position("MaxHealth"), float(health))

    def is_owned_by(self, owner: ObjectOwner):
        if self.owner.id_ is not None and self.owner.id_ == owner.id_:
            return True
        elif self.owner.player_name is not None and self.owner.player_name == owner.player_name:
            return True
        elif self.owner.tribe_name is not None and self.owner.tribe_name == owner.tribe_name:
            return True
        elif self.owner.tribe_id is not None and self.owner.tribe_id == owner.tribe_id:
            return True
        elif self.owner.original_placer_id is not None and self.owner.original_placer_id == owner.original_placer_id:
            return True
        return False
    
    # def set_owner(self, owner: ObjectOwner, save: AsaSave):
    #     self.owner = owner
    #     save.update_game_object(self.object)

    def __str__(self):
        return f"SimpleStructure: {self.owner.name} {self.id_} {self.current_health}/{self.max_health} {self.location}"
    
    def to_string_complete(self):
        parts = [
            f"Last in ally range time: {self.last_in_ally_range_time_serialized}",
            f"Owner: {self.owner}",
            f"Location: {self.location}",
            f"Max health: {self.max_health}",
            f"Current health: {self.current_health}",
            f"Linked structures: {self.linked_structures}",
            f"Linked structure uuids: {self.linked_structure_uuids}",
            f"Original creation time: {self.original_creation_time}",
            f"Last enter stasis time: {self.last_enter_stasis_time}",
            f"Has reset decay time: {self.has_reset_decay_time}",
            f"Saved when stasised: {self.saved_when_stasised}",
            f"Was placement snapped: {self.was_placement_snapped}",
            f"Last in ally range time serialized: {self.last_in_ally_range_time_serialized}",
        ]
        return "\n".join(parts)
        