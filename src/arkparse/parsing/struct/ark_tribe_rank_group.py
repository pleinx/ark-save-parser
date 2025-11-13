from dataclasses import dataclass
from typing import TYPE_CHECKING
import json

from arkparse.utils.json_utils import DefaultJsonEncoder

if TYPE_CHECKING:
    from ..ark_binary_parser import ArkBinaryParser

@dataclass
class ArkTribeRankGroup:
    name: str
    rank: int
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

    prevent_structure_demolish: bool
    prevent_structure_attachment: bool
    prevent_structure_build_in_range: bool
    prevent_unclaiming: bool
    allow_invites: bool
    limit_invites: bool
    allow_demotions: bool
    allow_promotions: bool
    allow_banishments: bool
    prevent_wireless_crafting: bool

    teleport_members_rank: int
    teleport_dinos_rank: int

    is_default_rank: bool
    allow_ping: bool
    allow_rally_point: bool


    def _read_byte_property(self, byte_buffer: "ArkBinaryParser", name: str) -> int:
        byte_buffer.validate_string(name)
        byte_buffer.validate_string("ByteProperty")
        present = byte_buffer.read_uint32() != 1

        if present:
            is_pos = byte_buffer.read_byte() == 1
            if is_pos:
                pos = byte_buffer.read_uint32()
            value = byte_buffer.read_byte()
            return value
        else:
            byte_buffer.validate_uint32(0)
            byte_buffer.validate_string("None")
            byte_buffer.validate_uint16(0)
    
    def _read_bool_property(self, byte_buffer: "ArkBinaryParser", name: str) -> bool:
        byte_buffer.validate_string(name)
        byte_buffer.validate_string("BoolProperty")
        byte_buffer.validate_uint32(0)
        byte_buffer.validate_uint32(0)
        value = byte_buffer.peek_u16()
        if value == 1 or value == 0:
            byte_buffer.read_uint16()
        else:
            value = byte_buffer.read_byte()
        return value != 0

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        byte_buffer.store()
        byte_buffer.validate_string("RankGroupName")
        byte_buffer.validate_string("StrProperty")
        byte_buffer.skip_bytes(9)
        length = byte_buffer.peek_int()
        if length != 0:
            self.name = byte_buffer.read_string()
        else:
            byte_buffer.skip_bytes(4)
            self.name = ""

        self.rank = self._read_byte_property(byte_buffer, "RankGroupRank")
        self.inventory_rank = self._read_byte_property(byte_buffer, "InventoryRank")
        self.structure_activation_rank = self._read_byte_property(byte_buffer, "StructureActivationRank")
        self.new_structure_activation_rank = self._read_byte_property(byte_buffer, "NewStructureActivationRank")
        self.new_structure_inventory_rank = self._read_byte_property(byte_buffer, "NewStructureInventoryRank")
        self.pet_order_rank = self._read_byte_property(byte_buffer, "PetOrderRank")
        self.pet_riding_rank = self._read_byte_property(byte_buffer, "PetRidingRank")
        self.invite_to_group_rank = self._read_byte_property(byte_buffer, "InviteToGroupRank")
        self.max_promotion_group_rank = self._read_byte_property(byte_buffer, "MaxPromotionGroupRank")
        self.max_demotion_group_rank = self._read_byte_property(byte_buffer, "MaxDemotionGroupRank")
        self.max_banishment_group_rank = self._read_byte_property(byte_buffer, "MaxBanishmentGroupRank")
        self.num_invites_remaining = self._read_byte_property(byte_buffer, "NumInvitesRemaining")

        self.prevent_structure_demolish = self._read_bool_property(byte_buffer, "bPreventStructureDemolish")
        self.prevent_structure_attachment = self._read_bool_property(byte_buffer, "bPreventStructureAttachment")
        self.prevent_structure_build_in_range = self._read_bool_property(byte_buffer, "bPreventStructureBuildInRange")
        self.prevent_unclaiming = self._read_bool_property(byte_buffer, "bPreventUnclaiming")
        self.allow_invites = self._read_bool_property(byte_buffer, "bAllowInvites")
        self.limit_invites = self._read_bool_property(byte_buffer, "bLimitInvites")
        self.allow_demotions = self._read_bool_property(byte_buffer, "bAllowDemotions")
        self.allow_promotions = self._read_bool_property(byte_buffer, "bAllowPromotions")
        self.allow_banishments = self._read_bool_property(byte_buffer, "bAllowBanishments")
        self.prevent_wireless_crafting = self._read_bool_property(byte_buffer, "bPreventWirelessCrafting")
        
        self.teleport_members_rank = self._read_byte_property(byte_buffer, "TeleportMembersRank")   
        self.teleport_dinos_rank = self._read_byte_property(byte_buffer, "TeleportDinosRank")

        self.is_default_rank = self._read_bool_property(byte_buffer, "bDefaultRank")
        self.allow_ping = self._read_bool_property(byte_buffer, "bAllowPing")
        self.allow_rally_point = self._read_bool_property(byte_buffer, "bAllowRallyPoint")

        byte_buffer.validate_string("None")

        print(self.to_json_str())

    def __str__(self) -> str:
        return (f"name:{self.name} rank:{self.rank} default:{self.is_default_rank}")
    
    def to_json_obj(self):
        return {
            "name": self.name,
            "rank": self.rank,
            "inventory_rank": self.inventory_rank,
            "structure_activation_rank": self.structure_activation_rank,
            "new_structure_activation_rank": self.new_structure_activation_rank,
            "new_structure_inventory_rank": self.new_structure_inventory_rank,
            "pet_order_rank": self.pet_order_rank,
            "pet_riding_rank": self.pet_riding_rank,
            "invite_to_group_rank": self.invite_to_group_rank,
            "max_promotion_group_rank": self.max_promotion_group_rank,
            "max_demotion_group_rank": self.max_demotion_group_rank,
            "max_banishment_group_rank": self.max_banishment_group_rank,
            "num_invites_remaining": self.num_invites_remaining,
            "prevent_structure_demolish": self.prevent_structure_demolish,
            "prevent_structure_attachment": self.prevent_structure_attachment,
            "prevent_structure_build_in_range": self.prevent_structure_build_in_range,
            "prevent_unclaiming": self.prevent_unclaiming,
            "allow_invites": self.allow_invites,
            "limit_invites": self.limit_invites,
            "allow_demotions": self.allow_demotions,
            "allow_promotions": self.allow_promotions,
            "allow_banishments": self.allow_banishments,
            "prevent_wireless_crafting": self.prevent_wireless_crafting,
            "teleport_members_rank": self.teleport_members_rank,
            "teleport_dinos_rank": self.teleport_dinos_rank,
            "is_default_rank": self.is_default_rank,
            "allow_ping": self.allow_ping,
            "allow_rally_point": self.allow_rally_point
        }
    
    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)


