import json
import math
from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.logging import ArkSaveLogger
from arkparse.object_model.cryopods.cryopod import Cryopod
from arkparse.object_model.dinos.dino import Dino
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.object_model.equipment import Weapon, Shield, Armor, Saddle
from arkparse.object_model.equipment.__equipment_with_armor import EquipmentWithArmor
from arkparse.object_model.equipment.__equipment_with_durability import EquipmentWithDurability
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.object_model import ArkGameObject
from arkparse.api import EquipmentApi, PlayerApi
from arkparse.parsing import ArkBinaryParser
from arkparse.parsing.struct.ark_item_net_id import ArkItemNetId
from arkparse.parsing.struct import ArkUniqueNetIdRepl
from arkparse.parsing.struct import ObjectReference
from arkparse.saves.asa_save import AsaSave
from arkparse.utils.json_utils import DefaultJsonEncoder

from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.equipment.__armor_defaults import _get_default_hypoT, _get_default_hyperT

def get_player_short_name(obj: ArkGameObject):
    to_strip_end = [
        "_C",
    ]

    short = obj.blueprint.split('/')[-1].split('.')[0]

    for strip in to_strip_end:
        if short.endswith(strip):
            short = short[:-len(strip)]

    return short

def get_actual_value(obj: ArkGameObject, stat: ArkEquipmentStat, internal_value: int) -> float:
    if stat == ArkEquipmentStat.ARMOR:
        d = EquipmentWithArmor.get_default_armor(obj.blueprint)
        return round(d * (0.0002 * internal_value + 1), 1)
    elif stat == ArkEquipmentStat.DURABILITY:
        d = EquipmentWithDurability.get_default_dura(obj.blueprint)
        return d * (0.00025 * internal_value + 1)
    elif stat == ArkEquipmentStat.DAMAGE:
        return round(100.0 + internal_value / 100, 1)
    elif stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
        if internal_value == 0:
            return 0
        d = _get_default_hypoT(obj.blueprint)
        return round(d * (0.0002 * internal_value + 1), 1)
    elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
        if internal_value == 0:
            return 0
        d = _get_default_hyperT(obj.blueprint)
        return round(d * (0.0002 * internal_value + 1), 1)
    else:
        raise ValueError(f"Stat {stat} is not valid for {obj.blueprint}")

def primal_item_to_json_obj(obj: ArkGameObject):
    item_id: ArkItemNetId = obj.get_property_value("ItemID")
    owner_in: ObjectReference = obj.get_property_value("OwnerInventory", default=ObjectReference())
    owner_inv_uuid = UUID(owner_in.value) if owner_in is not None and hasattr(owner_in, "value") and owner_in.value is not None else None
    result = { "UUID": obj.uuid.__str__() if obj.uuid is not None else None,
               "ItemNetId1": item_id.id1 if item_id is not None else None,
               "ItemNetId2": item_id.id2 if item_id is not None else None,
               "OwnerInventoryUUID": owner_inv_uuid.__str__() if owner_inv_uuid is not None else None,
               "ClassName": "item",
               "ItemArchetype": obj.blueprint }

    if obj.properties is not None and len(obj.properties) > 0:
        for prop in obj.properties:
            if prop is not None:
                if prop.name is not None and \
                        len(prop.name) > 0 and \
                        "CustomItemDatas" not in prop.name and \
                        "ItemID" not in prop.name and \
                        "OwnerInventory" not in prop.name:
                    prop_value = obj.get_property_value(prop.name, None)
                    if "NextSpoilingTime" in prop.name or "SavedDurability" in prop.name:
                        if math.isnan(prop.value):
                            prop_value = None
                    result[prop.name] = prop_value

    if "/PrimalItemArmor_" in obj.blueprint:
        armor = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.ARMOR.value, default=0)
        result["Armor"] = get_actual_value(obj, ArkEquipmentStat.ARMOR, armor)
        dura = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
        result["Durability"] = get_actual_value(obj, ArkEquipmentStat.DURABILITY, dura)
        if "Saddle" not in obj.blueprint:
            hypo = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPOTHERMAL_RESISTANCE.value, default=0)
            result["HypothermalResistance"] = get_actual_value(obj, ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, hypo)
            hyper = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPERTHERMAL_RESISTANCE.value, default=0)
            result["HyperthermalResistance"] = get_actual_value(obj, ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, hyper)

    if "/PrimalItem_" in obj.blueprint:
        damage = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.DAMAGE.value, default=0)
        result["Damage"] = get_actual_value(obj, ArkEquipmentStat.DAMAGE, damage)

    return result

class JsonApi:
    def __init__(self, save: AsaSave, ignore_error: bool = False):
        self.save = save
        self.ignore_error = ignore_error

    def __del__(self):
        self.save = None

    def export_armors(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting armors...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get armors.
        armors: Dict[UUID, Armor] = equipment_api.get_all(EquipmentApi.Classes.ARMOR)

        # Format armors into JSON.
        all_armors = []
        for armor in armors.values():
            all_armors.append(armor.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "armors.json", "w") as text_file:
            text_file.write(json.dumps(all_armors, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Armors successfully exported.")

    def export_weapons(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting weapons...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get weapons.
        weapons: Dict[UUID, Weapon] = equipment_api.get_all(EquipmentApi.Classes.WEAPON)

        # Format weapons into JSON.
        all_weapons = []
        for weapon in weapons.values():
            all_weapons.append(weapon.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "weapons.json", "w") as text_file:
            text_file.write(json.dumps(all_weapons, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Weapons successfully exported.")

    def export_shields(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting shields...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get shields.
        shields: Dict[UUID, Shield] = equipment_api.get_all(EquipmentApi.Classes.SHIELD)

        # Format shields into JSON.
        all_shields = []
        for shield in shields.values():
            all_shields.append(shield.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "shields.json", "w") as text_file:
            text_file.write(json.dumps(all_shields, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Shields successfully exported.")

    def export_saddles(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting saddles...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get saddles.
        saddles: Dict[UUID, Saddle] = equipment_api.get_all(EquipmentApi.Classes.SADDLE)

        # Format saddles into JSON.
        all_saddles = []
        for saddle in saddles.values():
            all_saddles.append(saddle.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "saddles.json", "w") as text_file:
            text_file.write(json.dumps(all_saddles, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Saddles successfully exported.")

    def export_player_pawns(self, player_api: PlayerApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting player pawns...")

        # Get player API if not provided.
        if player_api is None:
            player_api = PlayerApi(self.save, self.ignore_error)

        # Get player pawns.
        player_pawns: Dict[UUID, ArkGameObject] = player_api.pawns

        # Format player pawns into JSON.
        all_pawns = []
        for pawn_obj in player_pawns.values():
            pawn_obj_binary = self.save.get_game_obj_binary(pawn_obj.uuid)
            pawn: StructureWithInventory = StructureWithInventory(pawn_obj.uuid, ArkBinaryParser(pawn_obj_binary, save_context=self.save.save_context), self.save)
            if pawn.inventory is not None and pawn.inventory.object is not None:
                platform_profile_id: ArkUniqueNetIdRepl = pawn_obj.get_property_value("PlatformProfileID", None)
                pawn_data = { "UUID": pawn_obj.uuid.__str__() if pawn_obj.uuid is not None else None,
                              "InventoryUUID": pawn.inventory.object.uuid.__str__() if pawn.inventory.object.uuid is not None else None,
                              "ShortName": get_player_short_name(pawn_obj),
                              "ClassName": "player",
                              "ItemArchetype": pawn_obj.blueprint,
                              "PlayerUniqueNetID": platform_profile_id.value if platform_profile_id is not None else None,
                              "PlayerName": pawn_obj.get_property_value("PlayerName", None),
                              "PlatformProfileName": pawn_obj.get_property_value("PlatformProfileName", None),
                              "LinkedPlayerDataID": pawn_obj.get_property_value("LinkedPlayerDataID", None),
                              "TribeID": pawn_obj.get_property_value("TargetingTeam", None),
                              "TribeName": pawn_obj.get_property_value("TribeName", None),
                              "SavedSleepAnim": pawn_obj.get_property_value("SavedSleepAnim", None), # Last sleep time (Game Time in seconds)
                              "SavedLastTimeHadController": pawn_obj.get_property_value("SavedLastTimeHadController", None), # Last controlled time (Game Time in seconds)
                              "LastTimeUpdatedCharacterStatusComponent": pawn_obj.get_property_value("LastTimeUpdatedCharacterStatusComponent", None), # Last StatusComponent update time (Game Time in seconds)
                              "LastEnterStasisTime": pawn_obj.get_property_value("LastEnterStasisTime", None), # Last enter statis time (Game Time in seconds)
                              "OriginalCreationTime": pawn_obj.get_property_value("OriginalCreationTime", None), # Original creation time (Game Time in seconds)
                              "FacialHairIndex": pawn_obj.get_property_value("FacialHairIndex", None),
                              "HeadHairIndex": pawn_obj.get_property_value("HeadHairIndex", None),
                              "PercentOfFullHeadHairGrowth": pawn_obj.get_property_value("PercentOfFullHeadHairGrowth", None),
                              "bGaveInitialItems": pawn_obj.get_property_value("bGaveInitialItems", None),
                              "bIsSleeping": pawn_obj.get_property_value("bIsSleeping", None),
                              "bSavedWhenStasised": pawn_obj.get_property_value("bSavedWhenStasised", None),
                              "ActorTransformX": pawn_obj.location.x if pawn_obj.location is not None else None,
                              "ActorTransformY": pawn_obj.location.y if pawn_obj.location is not None else None,
                              "ActorTransformZ": pawn_obj.location.z if pawn_obj.location is not None else None }
                all_pawns.append(pawn_data)

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "player_pawns.json", "w") as text_file:
            text_file.write(json.dumps(all_pawns, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Player pawns successfully exported.")

    def export_dinos(self, export_folder_path: str = Path.cwd() / "json_exports", include_wilds: bool = True, include_tames: bool = True, include_cryopodded: bool = True):
        ArkSaveLogger.api_log("Exporting dinos...")

        # Parse and format dinos as JSON.
        all_dinos = []
        query = "SELECT key, value FROM game"
        with self.save.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                obj_uuid = self.save.byte_array_to_uuid(row[0])
                byte_buffer = ArkBinaryParser(row[1], self.save.save_context)
                class_name = byte_buffer.read_name()
                if class_name is None or ("PrimalItem_WeaponEmptyCryopod_C" not in class_name and not ("Dinos/" in class_name and "_Character_" in class_name)):
                    continue
                obj = self.save.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)
                if obj:
                    dino = None
                    if (include_tames or include_wilds) and "Dinos/" in obj.blueprint and "_Character_" in obj.blueprint:
                        is_tamed = obj.get_property_value("TamedTimeStamp") is not None
                        parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
                        if is_tamed:
                            if include_tames:
                                dino = TamedDino(obj.uuid, parser, self.save)
                        else:
                            if include_wilds:
                                dino = Dino(obj.uuid, parser, self.save)
                    elif include_cryopodded and "PrimalItem_WeaponEmptyCryopod_C" in obj.blueprint:
                        if not obj.get_property_value("bIsEngram", default=False):
                            cryopod = Cryopod(obj.uuid, ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context))
                            if cryopod.dino is not None:
                                dino = cryopod.dino
                    if dino is not None:
                        all_dinos.append(dino.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "dinos.json", "w") as text_file:
            text_file.write(json.dumps(all_dinos, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Dinos successfully exported.")

    def export_structures(self, export_folder_path: str = Path.cwd() / "json_exports", only_structures_with_inventory: bool = False):
        ArkSaveLogger.api_log("Exporting structures...")

        # Parse and format structures as JSON.
        all_structures = []
        query = "SELECT key, value FROM game"
        with self.save.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                obj_uuid = self.save.byte_array_to_uuid(row[0])
                byte_buffer = ArkBinaryParser(row[1], self.save.save_context)
                class_name = byte_buffer.read_name()
                if class_name is None or "/Structures" not in class_name or "PrimalItemStructure_" in class_name:
                    continue
                obj = self.save.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)
                if obj:
                    obj: ArkGameObject = obj
                    if obj is not None:
                        parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
                        if obj.get_property_value("MaxItemCount") is not None or (obj.get_property_value("MyInventoryComponent") is not None and obj.get_property_value("CurrentItemCount") is not None):
                            structure = StructureWithInventory(obj.uuid, parser, self.save)
                        else:
                            if only_structures_with_inventory:
                                continue
                            structure = Structure(obj.uuid, parser)
                        if obj.uuid in self.save.save_context.actor_transforms:
                            structure.set_actor_transform(self.save.save_context.actor_transforms[obj.uuid])
                        all_structures.append(structure.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "structures.json", "w") as text_file:
            text_file.write(json.dumps(all_structures, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Structures successfully exported.")

    def export_items(self, export_folder_path: str = Path.cwd() / "json_exports", include_engrams: bool = False):
        ArkSaveLogger.api_log("Exporting items...")

        # Parse and format items as JSON.
        all_items = []
        query = "SELECT key, value FROM game"
        with self.save.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                obj_uuid = self.save.byte_array_to_uuid(row[0])
                byte_buffer = ArkBinaryParser(row[1], self.save.save_context)
                class_name = byte_buffer.read_name()

                if "/PrimalItemArmor_" not in class_name and \
                        "/PrimalItem_" not in class_name and \
                        "/PrimalItemAmmo_" not in class_name and \
                        "/PrimalItemC4Ammo" not in class_name and \
                        "/PrimalItemResource_" not in class_name and \
                        "/DroppedItemGeneric_" not in class_name and \
                        "/PrimalItemConsumable_" not in class_name:
                    continue

                obj = self.save.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)
                if obj:
                    if (not include_engrams) and obj.get_property_value("bIsEngram"):
                        continue
                    all_items.append(primal_item_to_json_obj(obj))

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "items.json", "w") as text_file:
            text_file.write(json.dumps(all_items, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Items successfully exported.")

    def export_all(self,
                   equipment_api: EquipmentApi = None,
                   player_api: PlayerApi = None,
                   export_folder_path: str = Path.cwd() / "json_exports"):
        self.export_armors(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_weapons(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_shields(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_saddles(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_player_pawns(player_api=player_api, export_folder_path=export_folder_path)
        self.export_items(export_folder_path=export_folder_path)
        self.export_dinos(export_folder_path=export_folder_path)
        self.export_structures(export_folder_path=export_folder_path)
