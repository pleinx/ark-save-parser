import json
import os
import math
from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.object_model.cryopods.cryopod import Cryopod
from arkparse.object_model.dinos.dino import Dino
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.object_model.equipment import Weapon, Shield, Armor, Saddle
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
from arkparse.object_model.equipment.__equipment_with_armor import _get_default_armor
from arkparse.object_model.equipment.__equipment_with_durability import _get_default_dura

@staticmethod
def get_player_short_name(obj: ArkGameObject):
    to_strip_end = [
        "_C",
    ]

    short = obj.blueprint.split('/')[-1].split('.')[0]

    for strip in to_strip_end:
        if short.endswith(strip):
            short = short[:-len(strip)]

    return short

@staticmethod
def get_player_unique_net_id(obj: ArkGameObject):
    platform_profile_id: ArkUniqueNetIdRepl = obj.get_property_value("PlatformProfileID", None)
    return platform_profile_id.value if platform_profile_id is not None else None

@staticmethod
def get_actual_value(object: ArkGameObject, stat: ArkEquipmentStat, internal_value: int) -> float:
    if stat == ArkEquipmentStat.ARMOR:
        d = _get_default_armor(object.blueprint)
        return round(d * (0.0002 * internal_value + 1), 1)
    elif stat == ArkEquipmentStat.DURABILITY:
        d = _get_default_dura(object.blueprint)
        return d * (0.00025 * internal_value + 1)
    elif stat == ArkEquipmentStat.DAMAGE:
        return round(100.0 + internal_value / 100, 1)
    elif stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
        if internal_value == 0:
            return 0
        d = _get_default_hypoT(object.blueprint)
        return round(d * (0.0002 * internal_value + 1), 1)
    elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
        if internal_value == 0:
            return 0
        d = _get_default_hyperT(object.blueprint)
        return round(d * (0.0002 * internal_value + 1), 1)
    else:
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")

@staticmethod
def primalItemToJsonObj(object: ArkGameObject):
    itemID: ArkItemNetId = object.get_property_value("ItemID")
    owner_in: ObjectReference = object.get_property_value("OwnerInventory", default=ObjectReference())
    owner_inv_uuid = UUID(owner_in.value) if owner_in is not None else None
    result = { "UUID": object.uuid.__str__() if object.uuid is not None else None,
               "UUID2": object.uuid2.__str__() if object.uuid2 is not None else None,
               "ItemNetId1": itemID.id1 if itemID is not None else None,
               "ItemNetId2": itemID.id2 if itemID is not None else None,
               "OwnerInventoryUUID": owner_inv_uuid.__str__() if owner_inv_uuid is not None else None,
               "ClassName": "item",
               "ItemArchetype": object.blueprint }

    if object.properties is not None and len(object.properties) > 0:
        for prop in object.properties:
            if prop is not None:
                if prop.name is not None and \
                        len(prop.name) > 0 and \
                        "CustomItemDatas" not in prop.name and \
                        "ItemID" not in prop.name and \
                        "OwnerInventory" not in prop.name:
                    #print("Prop: " + prop.name)
                    prop_value = object.get_property_value(prop.name, None)
                    #test = json.dumps(prop_value, indent=4, cls=DefaultJsonEncoder)
                    if "NextSpoilingTime" in prop.name or "SavedDurability" in prop.name:
                        if math.isnan(prop.value):
                            prop_value = None
                    result[prop.name] = prop_value

    if "/PrimalItemArmor_" in object.blueprint:
        armor = object.get_property_value("ItemStatValues", position=ArkEquipmentStat.ARMOR.value, default=0)
        result["Armor"] = get_actual_value(object, ArkEquipmentStat.ARMOR, armor)
        dura = object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
        result["Durability"] = get_actual_value(object, ArkEquipmentStat.DURABILITY, dura)
        hypo = object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPOTHERMAL_RESISTANCE.value, default=0)
        result["HypothermalResistance"] = get_actual_value(object, ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, hypo)
        hyper = object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPERTHERMAL_RESISTANCE.value, default=0)
        result["HyperthermalResistance"] = get_actual_value(object, ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, hyper)

    if "/PrimalItem_" in object.blueprint:
        damage = object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DAMAGE.value, default=0)
        result["Damage"] = get_actual_value(object, ArkEquipmentStat.DAMAGE, damage)

    return result

class JsonApi:
    def __init__(self, save: AsaSave, ignore_error: bool = False):
        self.save = save
        self.ignore_error = ignore_error

    def __del__(self):
        self.save = None

    def export_armors(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        print("Exporting armors...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get armors.
        armors: Dict[UUID, Armor] = equipment_api.get_all(EquipmentApi.Classes.ARMOR)

        # Format armors into JSON.
        allarmors = []
        for armor in armors.values():
            allarmors.append(armor.toJsonObj())

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "armors.json", "w") as text_file:
            text_file.write(json.dumps(allarmors, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_weapons(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        print("Exporting weapons...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get weapons.
        weapons: Dict[UUID, Weapon] = equipment_api.get_all(EquipmentApi.Classes.WEAPON)

        # Format weapons into JSON.
        allweapons = []
        for weapon in weapons.values():
            allweapons.append(weapon.toJsonObj())

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "weapons.json", "w") as text_file:
            text_file.write(json.dumps(allweapons, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_shields(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        print("Exporting shields...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get shields.
        shields: Dict[UUID, Shield] = equipment_api.get_all(EquipmentApi.Classes.SHIELD)

        # Format shields into JSON.
        allshields = []
        for shield in shields.values():
            allshields.append(shield.toJsonObj())

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "shields.json", "w") as text_file:
            text_file.write(json.dumps(allshields, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_saddles(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        print("Exporting saddles...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get saddles.
        saddles: Dict[UUID, Saddle] = equipment_api.get_all(EquipmentApi.Classes.SADDLE)

        # Format saddles into JSON.
        allsaddles = []
        for saddle in saddles.values():
            allsaddles.append(saddle.toJsonObj())

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "saddles.json", "w") as text_file:
            text_file.write(json.dumps(allsaddles, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_player_pawns(self, player_api: PlayerApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        print("Exporting player pawns...")

        # Get player API if not provided.
        if player_api is None:
            player_api = PlayerApi(self.save, self.ignore_error)

        # Get player pawns.
        player_pawns: Dict[UUID, ArkGameObject] = player_api.pawns

        # Format player pawns into JSON.
        allpawns = []
        for pawn_obj in player_pawns.values():
            pawn_obj_binary = self.save.get_game_obj_binary(pawn_obj.uuid)
            pawn: StructureWithInventory = StructureWithInventory(pawn_obj.uuid, ArkBinaryParser(pawn_obj_binary, save_context=self.save.save_context), self.save)
            if pawn.inventory is not None and pawn.inventory.object is not None:
                pawn_data = { "UUID": pawn_obj.uuid.__str__() if pawn_obj.uuid is not None else None,
                              "UUID2": pawn_obj.uuid2.__str__() if pawn_obj.uuid2 is not None else None,
                              "InventoryUUID": pawn.inventory.object.uuid.__str__() if pawn.inventory.object.uuid is not None else None,
                              "ShortName": get_player_short_name(pawn_obj),
                              "ClassName": "player",
                              "ItemArchetype": pawn_obj.blueprint,
                              "PlayerUniqueNetID": get_player_unique_net_id(pawn_obj),
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
                allpawns.append(pawn_data)

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "player_pawns.json", "w") as text_file:
            text_file.write(json.dumps(allpawns, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_dinos(self, export_folder_path: str = Path.cwd() / "json_exports", include_wilds: bool = True, include_tames: bool = True, include_cryopodded: bool = True):
        print("Exporting dinos...")

        # Parse and format dinos as JSON.
        alldinos = []
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
                        alldinos.append(dino.toJsonObj())

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "dinos.json", "w") as text_file:
            text_file.write(json.dumps(alldinos, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_structures(self, export_folder_path: str = Path.cwd() / "json_exports", only_structures_with_inventory: bool = False):
        print("Exporting structures...")

        # Parse and format structures as JSON.
        allstructures = []
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
                        allstructures.append(structure.toJsonObj())

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "structures.json", "w") as text_file:
            text_file.write(json.dumps(allstructures, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_items(self, export_folder_path: str = Path.cwd() / "json_exports", include_engrams: bool = False):
        allitems = []
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
                        "/PrimalItemC4Ammo" not in class_name:
                    continue

                obj = self.save.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)
                if obj:
                    if (not include_engrams) and obj.get_property_value("bIsEngram"):
                        continue
                    #parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
                    allitems.append(primalItemToJsonObj(obj))

        # Create json exports folder if it does not exists.
        if not os.path.exists(export_folder_path):
            os.makedirs(export_folder_path, exist_ok=True)

        # Write JSON.
        with open(export_folder_path / "items.json", "w") as text_file:
            text_file.write(json.dumps(allitems, indent=4, cls=DefaultJsonEncoder))

        print("Done")

    def export_all(self,
                   equipment_api: EquipmentApi = None,
                   player_api: PlayerApi = None,
                   export_folder_path: str = Path.cwd() / "json_exports"):
        self.export_armors(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_weapons(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_shields(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_saddles(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_player_pawns(player_api=player_api, export_folder_path=export_folder_path)
        self.export_dinos(export_folder_path=export_folder_path)
        self.export_structures(export_folder_path=export_folder_path)
