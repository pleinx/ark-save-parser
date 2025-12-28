from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ark_binary_parser import ArkBinaryParser

from arkparse.logging import ArkSaveLogger

@dataclass
class ArkTribeRankGroup:
    rank_group_name: str
    rank_group_rank: int
    inventory_rank: int
    structure_activation_rank: int
    new_structure_activation_rank: int
    new_structure_inventory_rank: int
    pet_order_rank: int
    pet_riding_rank: int
    invite_to_group_rank: int
    max_promotion_group_rank: int
    max_demotion_group_rank: int
    max_banishment_group_rank: int
    num_invites_remaining: int
    b_prevent_structure_demolish: bool
    b_prevent_structure_attachment: bool
    b_prevent_structure_build_in_range: bool
    b_prevent_unclaiming: bool
    b_allow_invites: bool
    b_limit_invites: bool
    b_allow_demotions: bool
    b_allow_promotions: bool
    b_allow_banishments: bool
    b_prevent_wireless_crafting: bool
    teleport_members_rank: int
    teleport_dinos_rank: int
    b_default_rank: bool
    b_allow_ping: bool
    b_allow_rally_point: bool

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        self.rank_group_name = byte_buffer.parse_string_property("RankGroupName")
        self.rank_group_rank = byte_buffer.parse_byte_property("RankGroupRank")
        self.inventory_rank = byte_buffer.parse_byte_property("InventoryRank")
        self.structure_activation_rank = byte_buffer.parse_byte_property("StructureActivationRank")
        self.new_structure_activation_rank = byte_buffer.parse_byte_property("NewStructureActivationRank")
        self.new_structure_inventory_rank = byte_buffer.parse_byte_property("NewStructureInventoryRank")
        self.pet_order_rank = byte_buffer.parse_byte_property("PetOrderRank")
        self.pet_riding_rank = byte_buffer.parse_byte_property("PetRidingRank")
        self.invite_to_group_rank = byte_buffer.parse_byte_property("InviteToGroupRank")
        self.max_promotion_group_rank = byte_buffer.parse_byte_property("MaxPromotionGroupRank")
        self.max_demotion_group_rank = byte_buffer.parse_byte_property("MaxDemotionGroupRank")
        self.max_banishment_group_rank = byte_buffer.parse_byte_property("MaxBanishmentGroupRank")
        self.num_invites_remaining = byte_buffer.parse_byte_property("NumInvitesRemaining")
        self.b_prevent_structure_demolish = byte_buffer.parse_boolean_property("bPreventStructureDemolish")
        self.b_prevent_structure_attachment = byte_buffer.parse_boolean_property("bPreventStructureAttachment")
        self.b_prevent_structure_build_in_range = byte_buffer.parse_boolean_property("bPreventStructureBuildInRange")
        self.b_prevent_unclaiming = byte_buffer.parse_boolean_property("bPreventUnclaiming")
        self.b_allow_invites = byte_buffer.parse_boolean_property("bAllowInvites")
        self.b_limit_invites = byte_buffer.parse_boolean_property("bLimitInvites")
        self.b_allow_demotions = byte_buffer.parse_boolean_property("bAllowDemotions")
        self.b_allow_promotions = byte_buffer.parse_boolean_property("bAllowPromotions")
        self.b_allow_banishments = byte_buffer.parse_boolean_property("bAllowBanishments")
        self.b_prevent_wireless_crafting = byte_buffer.parse_boolean_property("bPreventWirelessCrafting")
        self.teleport_members_rank = byte_buffer.parse_byte_property("TeleportMembersRank")
        self.teleport_dinos_rank = byte_buffer.parse_byte_property("TeleportDinosRank")
        self.b_default_rank = byte_buffer.parse_boolean_property("bDefaultRank")
        self.b_allow_ping = byte_buffer.parse_boolean_property("bAllowPing")
        self.b_allow_rally_point = byte_buffer.parse_boolean_property("bAllowRallyPoint")

        byte_buffer.validate_string("None")

        ArkSaveLogger.parser_log(f"Read tribe rank group: {self}")

    def __str__(self) -> str:
        return f"group_name:{self.rank_group_name} group_rank:{self.rank_group_rank}"
