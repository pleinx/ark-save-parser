from typing import List
from dataclasses import dataclass, field

from arkparse.parsing import ArkProperty
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing.struct import ObjectReference

@dataclass
class ArkStatPoints:
    health: int = 0
    stamina: int = 0
    torpidity: int = 0
    oxygen: int = 0
    food: int = 0
    water: int = 0
    temperature: int = 0
    weight: int = 0
    melee_damage: int = 0
    movement_speed: int = 0
    fortitude: int = 0
    crafting_speed: int = 0  # Optional: Adjust if not present

    def __init__(self, properties: List[ArkProperty]):
        # Define a mapping from property position to stat attribute
        position_map = {
            0: 'health',
            1: 'stamina',
            2: 'torpidity',
            3: 'oxygen',
            4: 'food',
            5: 'water',
            6: 'temperature',
            7: 'weight',
            8: 'melee_damage',
            9: 'movement_speed',
            10: 'fortitude',
            11: 'crafting_speed'
        }

        for prop in properties:
            if prop.type not in ["Byte", "Int"]:
                continue  # Skip properties of unexpected types
            stat_name = position_map.get(prop.position)
            if stat_name:
                setattr(self, stat_name, prop.value)

    def __str__(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"torpidity={self.torpidity}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"water={self.water}",
            f"temperature={self.temperature}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
            f"movement_speed={self.movement_speed}",
            f"fortitude={self.fortitude}",
            f"crafting_speed={self.crafting_speed}",
        ]
        return f"ArkStatPoints(points added)([{', '.join(stats)}])"


@dataclass
class ArkCharacterStats:
    level: int = 0
    experience: float = 0.0
    engram_points: int = 0
    explorer_notes: List[int] = field(default_factory=list)
    emotes: List[str] = field(default_factory=list)
    engrams: List[str] = field(default_factory=list)
    stats: ArkStatPoints = field(default_factory=lambda: ArkStatPoints([]))

    def __init__(self, properties: ArkPropertyContainer):

        # Find the main struct property, assumed to be "MyPersistentCharacterStats"
        main_stats_prop = properties.find_property("MyPersistentCharacterStats")
        if not main_stats_prop:
            raise ValueError("Missing 'MyPersistentCharacterStats' property.")
        if main_stats_prop.type != "Struct":
            raise ValueError("'MyPersistentCharacterStats' is not of type 'Struct'.")

        # Assuming 'value' contains another ArkPropertyContainer or a dict with 'properties'
        if not isinstance(main_stats_prop.value, ArkPropertyContainer):
            raise ValueError("'MyPersistentCharacterStats' value is not an ArkPropertyContainer.")

        main_properties = main_stats_prop.value

        # Parse level
        level_prop = main_properties.find_property("CharacterStatusComponent_ExtraCharacterLevel")
        if not level_prop:
            self.level = 1
        else:
            self.level = 1 + level_prop.value if level_prop.type in ["UInt16", "Int"] else 0

        # Parse experience
        experience_prop = main_properties.find_property("CharacterStatusComponent_ExperiencePoints")
        if not experience_prop:
            raise ValueError("Missing 'CharacterStatusComponent_ExperiencePoints' property.")
        self.experience = experience_prop.value if experience_prop.type == "Float" else 0.0

        # Parse engram_points
        engram_points_prop = main_properties.find_property("PlayerState_TotalEngramPoints")
        if not engram_points_prop:
            self.engram_points = 0
        else:
            self.engram_points = engram_points_prop.value if engram_points_prop.type == "Int" else 0

        # Parse explorer_notes
        explorer_notes_prop = main_properties.find_property("PerMapExplorerNoteUnlocks")
        if explorer_notes_prop and explorer_notes_prop.type == "Array":
            self.explorer_notes = explorer_notes_prop.value
        else:
            self.explorer_notes = []

        # Parse emotes
        emotes_prop = main_properties.find_property("EmoteUnlocks")
        if emotes_prop and emotes_prop.type == "Array":
            self.emotes = emotes_prop.value
        else:
            self.emotes = []

        # Parse engrams
        self.engrams = []
        engrams_prop = main_properties.find_property("PlayerState_EngramBlueprints")
        if engrams_prop and engrams_prop.type == "Array":
            # Extract the 'value' from each dictionary in the array
            for item in engrams_prop.value:
                item : ObjectReference = item
                self.engrams.append(item.value)
        else:
            self.engrams = []

        # Parse stats
        stat_points_props = main_properties.find_all_properties_of_name("CharacterStatusComponent_NumberOfLevelUpPointsApplied")
        if stat_points_props:
            self.stats = ArkStatPoints(stat_points_props)
        else:
            self.stats = ArkStatPoints([])

    def __str__(self):
        """
        Returns a compact string representation of ArkCharacterStats.

        Returns:
            str: String representation of the character stats.
        """
        parts = [
            "ArkCharacterStats:",
            f"  Level: {self.level}",
            f"  Experience: {self.experience}",
            f"  Engram Points: {self.engram_points}",
            f"  Explorer Notes: {self.explorer_notes}",
            f"  Emotes: {self.emotes}",
            f"  Engrams: {len(self.engrams)} engrams",
            f"  Stats: {self.stats}"
        ]
        return "\n".join(parts)
