from arkparse.parsing.struct.struct_val_check import check_uint32, check_byte, check_save_name, read_int32, read_float, read_string, read_double
from ....ark_binary_data import ArkBinaryParser
from ....ark_save_utils import ArkSaveLogger
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.object_model import ArkGameObject
from arkparse.parsing import ArkProperty
from arkparse.parsing.struct.ark_vector import ArkVector

from uuid import UUID
from dataclasses import dataclass

@dataclass
class EggStats:
    health: int = 0
    stamina: int = 0
    oxygen: int = 0
    food: int = 0
    weight: int = 0
    melee_damage: int = 0

    def set_stat(self, stat_index, value):
        if stat_index == 0:
            self.health = value
        elif stat_index == 1:
            self.stamina = value
        elif stat_index == 3:
            self.oxygen = value
        elif stat_index == 4:
            self.food = value
        elif stat_index == 7:
            self.weight = value
        elif stat_index == 8:
            self.melee_damage = value

    def get_level(self):
        return self.health + self.stamina + self.oxygen + self.food + self.weight + self.melee_damage + 1
    

class FertilizedEgg(ArkGameObject):
    type: str
    item_id : "ArkItemNetId"
    creation_time: float
    item_rating: float
    custom_description: str
    owner_uuid: UUID

    saved_durability: float
    last_durability_decrease_time: float
    next_spoil_time: float
    last_spoil_time: float

    original_drop_location : ArkVector

    levels: EggStats
    colors: list
    gender_override: int
    gene_traits: list
    tamed_ineffectiveness_modifier: float

    ancestors : list

    uuid_maybe: UUID

    def __init__(self, uuid: UUID, class_name: str, buffer: ArkBinaryParser):
        super().__init__(uuid, class_name, buffer)
        self.name = self.decode_name(buffer)
        check_byte(buffer, 0x01)

        start = class_name.find("Consumable") + len("Consumable")
        end = class_name.find("_C")
        if start != -1 and end != -1:
            self.type = class_name[start:end]
        else:
            self.type = "Unknown"
            raise Exception(f"Unknown Consumable type {class_name}")
        

        self.item_id = ArkProperty.read_property(buffer, False)
        self.item_rating = read_float(buffer, "ItemRating")      
        self.custom_description = read_string(buffer, "CustomItemDescription")

        self.owner_uuid = ArkProperty.read_property(buffer, False).value.value if buffer.peek_name() == "OwnerInventory" else None

        self.saved_durability = read_float(buffer, "SavedDurability")
        self.creation_time = read_double(buffer, "CreationTime")
        self.last_durability_decrease_time = read_double(buffer, "LastAutoDurabilityDecreaseTime")

        self.original_drop_location = ArkProperty.read_property(buffer, False).value if buffer.peek_name() == "OriginalItemDropLocation" else None

        self.next_spoil_time = read_double(buffer, "NextSpoilingTime")
        self.last_spoil_time = read_double(buffer, "LastSpoilingTime")

        self.levels = EggStats()
        for _ in range(6):
            check_save_name(buffer, f"EggNumberOfLevelUpPointsApplied")
            check_save_name(buffer, f"ByteProperty")
            check_uint32(buffer, 1)
            stat_index = buffer.read_uint32()
            check_save_name(buffer, f"None")
            check_byte(buffer, 0)
            value = buffer.read_byte()
            self.levels.set_stat(stat_index, value)

        self.tamed_ineffectiveness_modifier = read_float(buffer, "EggTamedIneffectivenessModifier") if buffer.peek_name() == "EggTamedIneffectivenessModifier" else 1.0

        self.egg_colors = []
        for i in range(6):
            check_save_name(buffer, f"EggColorSetIndices")
            check_save_name(buffer, f"ByteProperty")
            check_uint32(buffer, 1)
            check_uint32(buffer, i)
            check_save_name(buffer, f"None")
            check_byte(buffer, 0)
            value = buffer.read_byte()
            self.egg_colors.append(value)

        self.gender_override = read_int32(buffer, "EggGenderOverride")
        self.gene_traits = [t for t in ArkProperty.read_property(buffer, False).value]

        name = buffer.peek_name()
        if name == "EggDinoAncestors":
            self.ancestors = ArkProperty.read_property(buffer, False).value
        else:
            self.ancestors = []

        self.uuid_maybe = buffer.read_uuid()

        ArkSaveLogger.debug_log(f"Finished reading:\n {self}")

    def __str__(self) -> str:
        return str.join('', [f"Fertilized egg {self.type}\n",
                            f" with id {self.item_id}\n",
                            f" created at {self.creation_time}\n",
                            f" with rating {self.item_rating}\n",
                            f" and description \'{self.custom_description}\'\n",
                            f" owned by {self.owner_uuid}\n",
                            f" with durability {self.saved_durability}\n",
                            f" last durability decrease at {self.last_durability_decrease_time}\n",
                            f" next spoil at {self.next_spoil_time}\n",
                            f" last spoil at {self.last_spoil_time}\n",
                            f" at location {self.original_drop_location}\n",
                            f" with levels {self.levels}\n",
                            f" and colors {self.egg_colors}\n",
                            f" and traits {self.gene_traits}\n",
                            f" and ancestors {self.ancestors}\n",
        ])