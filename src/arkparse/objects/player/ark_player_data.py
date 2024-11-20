from typing import List
from dataclasses import dataclass

from arkparse.parsing import ArkPropertyContainer
from arkparse.struct import ArkVectorBoolPair, ArkTrackedActorIdCategoryPairWithBool, ArkMyPersistentBuffDatas

from .ark_character_config import ArkCharacterConfig
from .ark_character_stats import ArkCharacterStats

@dataclass
class ArkPlayerData:
    name: str
    char_name: str
    tribe: int

    nr_of_deaths: int
    death_locations: List[ArkVectorBoolPair]

    waypoints: List[ArkTrackedActorIdCategoryPairWithBool]

    id_: int
    unique_id: str
    ip_address: str
    first_spawned: bool

    player_data_version: int

    next_allowed_respawn_time: float
    last_time_died: float
    login_time: float
    allowed_respawn_interval: float
    spawn_day_nr: int
    spawn_day_time: float

    config: ArkCharacterConfig
    stats: ArkCharacterStats

    persistent_buff_data = ArkMyPersistentBuffDatas

    def __init__(self, props: ArkPropertyContainer):
        # Parse 'SavedPlayerDataVersion'
        saved_player_data_version_prop = props.find_property("SavedPlayerDataVersion")
        if not saved_player_data_version_prop:
            raise ValueError("Missing 'SavedPlayerDataVersion' property.")
        if saved_player_data_version_prop.type != "Int":
            raise ValueError("'SavedPlayerDataVersion' property is not of type 'Int'.")
        self.player_data_version = saved_player_data_version_prop.value

        # Parse 'MyData'
        my_data_prop = props.find_property("MyData")
        if not my_data_prop:
            raise ValueError("Missing 'MyData' property.")
        if my_data_prop.type != "Struct":
            raise ValueError("'MyData' property is not of type 'Struct'.")
        if not isinstance(my_data_prop.value, ArkPropertyContainer):
            raise ValueError("'MyData' property value is not an ArkPropertyContainer.")

        my_data = my_data_prop.value

        # Parse 'PlayerDataID' -> id_
        player_data_id_prop = my_data.find_property("PlayerDataID")
        if not player_data_id_prop:
            raise ValueError("Missing 'PlayerDataID' property.")
        if player_data_id_prop.type not in ["UInt64", "Int"]:
            raise ValueError("'PlayerDataID' property is not of type 'UInt64' or 'Int'.")
        self.id_ = player_data_id_prop.value


        # Parse 'PlayerCharacterName' -> char_name
        player_character_name_prop = my_data.find_property("PlayerCharacterName")
        if not player_character_name_prop:
            raise ValueError("Missing 'PlayerCharacterName' property.")
        if player_character_name_prop.type != "String":
            raise ValueError("'PlayerCharacterName' property is not of type 'String'.")
        self.char_name = player_character_name_prop.value
        

        # Parse 'UniqueID' -> unique_id
        unique_id_prop = my_data.find_property("UniqueID")
        if not unique_id_prop:
            raise ValueError("Missing 'UniqueID' property.")
        if unique_id_prop.type != "Struct":
            raise ValueError("'UniqueID' property is not of type 'Struct'.")
        self.unique_id = unique_id_prop.value.value
        

        # Parse 'SavedNetworkAddress' -> ip_address
        saved_network_address_prop = my_data.find_property("SavedNetworkAddress")
        if not saved_network_address_prop:
            raise ValueError("Missing 'SavedNetworkAddress' property.")
        if saved_network_address_prop.type != "String":
            raise ValueError("'SavedNetworkAddress' property is not of type 'String'.")
        self.ip_address = saved_network_address_prop.value

        # Parse 'PlayerName' -> name
        player_name_prop = my_data.find_property("PlayerName")
        if not player_name_prop:
            raise ValueError("Missing 'PlayerName' property.")
        if player_name_prop.type != "String":
            raise ValueError("'PlayerName' property is not of type 'String'.")
        self.name = player_name_prop.value

        # Parse 'bFirstSpawned' -> first_spawned
        first_spawned_prop = my_data.find_property("bFirstSpawned")
        if not first_spawned_prop:
            raise ValueError("Missing 'bFirstSpawned' property.")
        if first_spawned_prop.type != "Boolean":
            raise ValueError("'bFirstSpawned' property is not of type 'Boolean'.")
        self.first_spawned = first_spawned_prop.value

        self.config = ArkCharacterConfig(props)
        self.stats = ArkCharacterStats(props)


        # Parse 'TribeID' -> tribe
        tribe_id_prop = props.find_property("TribeID")
        if not tribe_id_prop:
            self.tribe = 0
            # raise ValueError("Missing 'TribeID' property.")
        else:
            if tribe_id_prop.type != "Int":
                raise ValueError("'TribeID' property is not of type 'Int'.")
            self.tribe = tribe_id_prop.value

        # Parse 'NextAllowedRespawnTime' -> next_allowed_respawn_time
        next_allowed_respawn_time_prop = props.find_property("NextAllowedRespawnTime")
        if not next_allowed_respawn_time_prop:
            self.next_allowed_respawn_time = 0.0
            # raise ValueError("Missing 'NextAllowedRespawnTime' property.")
        else:
            if next_allowed_respawn_time_prop.type != "Double":
                raise ValueError("'NextAllowedRespawnTime' property is not of type 'Double'.")
            self.next_allowed_respawn_time = next_allowed_respawn_time_prop.value

        # Parse 'LastTimeDiedToEnemyTeam' -> last_time_died
        last_time_died_prop = props.find_property("LastTimeDiedToEnemyTeam")
        if not last_time_died_prop:
            self.last_time_died = 0.0
        else:
            # raise ValueError("Missing 'LastTimeDiedToEnemyTeam' property.")
            if last_time_died_prop.type != "Double":
                raise ValueError("'LastTimeDiedToEnemyTeam' property is not of type 'Double'.")
            self.last_time_died = last_time_died_prop.value

        # Parse 'LoginTime' -> login_time
        login_time_prop = props.find_property("LoginTime")
        if not login_time_prop:
            raise ValueError("Missing 'LoginTime' property.")
        if login_time_prop.type != "Double":
            raise ValueError("'LoginTime' property is not of type 'Double'.")
        self.login_time = login_time_prop.value

        # Parse 'AllowedRespawnInterval' -> allowed_respawn_interval
        allowed_respawn_interval_prop = props.find_property("AllowedRespawnInterval")
        if not allowed_respawn_interval_prop:
            self.allowed_respawn_interval = 0.0
            # raise ValueError("Missing 'AllowedRespawnInterval' property.")
        else:
            if allowed_respawn_interval_prop.type != "Float":
                raise ValueError("'AllowedRespawnInterval' property is not of type 'Float'.")
            self.allowed_respawn_interval = allowed_respawn_interval_prop.value

        # Parse 'NumOfDeaths' -> nr_of_deaths
        num_of_deaths_prop = props.find_property("NumOfDeaths")
        if not num_of_deaths_prop:
            self.nr_of_deaths = 0
            # raise ValueError("Missing 'NumOfDeaths' property.")
        else:
            if num_of_deaths_prop.type != "Float":
                raise ValueError("'NumOfDeaths' property is not of type 'Float'.")
            self.nr_of_deaths = int(num_of_deaths_prop.value)

        # Parse 'SpawnDayNumber' -> spawn_day_nr
        spawn_day_number_prop = props.find_property("SpawnDayNumber")
        if not spawn_day_number_prop:
            raise ValueError("Missing 'SpawnDayNumber' property.")
        if spawn_day_number_prop.type != "Int":
            raise ValueError("'SpawnDayNumber' property is not of type 'Int'.")
        self.spawn_day_nr = spawn_day_number_prop.value

        # Parse 'SpawnDayTime' -> spawn_day_time
        spawn_day_time_prop = props.find_property("SpawnDayTime")
        if not spawn_day_time_prop:
            raise ValueError("Missing 'SpawnDayTime' property.")
        if spawn_day_time_prop.type != "Float":
            raise ValueError("'SpawnDayTime' property is not of type 'Float'.")
        self.spawn_day_time = spawn_day_time_prop.value

        # Parse 'ServerSavedLastDeathLocations' -> death_locations
        death_locations_prop = props.find_property("ServerSavedLastDeathLocations")
        if death_locations_prop and death_locations_prop.type == "Array":
            self.death_locations = []
            for item in death_locations_prop.value:
                self.death_locations.append(item)
        else:
            self.death_locations = []

        # Parse 'SavedWaypointTrackedActorInfo' -> waypoints
        waypoints_prop = props.find_property("SavedWaypointTrackedActorInfo")
        if waypoints_prop and waypoints_prop.type == "Array":
            self.waypoints = []
            for item in waypoints_prop.value:
                self.waypoints.append(item)
        else:
            self.waypoints = []

        # Parse 'MyPersistentBuffData' -> persistent_buff_data
        persistent_buff_data_prop = props.find_property("MyPersistentBuffDatas")
        if persistent_buff_data_prop and persistent_buff_data_prop.type == "Struct":
            self.persistent_buff_data = persistent_buff_data_prop.value
        else:
            self.persistent_buff_data = None

    def __str__(self):
        """
        Returns a comprehensive, compact string representation of ArkPlayerData.
        
        Returns:
            str: String representation of the ArkPlayerData instance.
        """
        parts = [
            "ArkPlayerData:",
            f"  Name: {self.name}",
            f"  Character Name: {self.char_name}",
            f"  Unreal engine ID: {self.unique_id}",
            f"  Tribe ID: {self.tribe}",
            f"  Number of Deaths: {self.nr_of_deaths}",
            f"  Death Locations: [{', '.join(str(dl) for dl in self.death_locations)}]",
            f"  Waypoints: [{', '.join(str(wp) for wp in self.waypoints)}]",
            f"  Player Data Version: {self.player_data_version}",
            f"  ID: {self.id_}",
            f"  IP Address: {self.ip_address}",
            f"  First Spawned: {self.first_spawned}",
            f"  Next Allowed Respawn Time: {self.next_allowed_respawn_time}",
            f"  Last Time Died: {self.last_time_died}",
            f"  Login Time: {self.login_time}",
            f"  Allowed Respawn Interval: {self.allowed_respawn_interval}",
            f"  Spawn Day Number: {self.spawn_day_nr}",
            f"  Spawn Day Time: {self.spawn_day_time}",
            f"  Config: {self.config}",
            f"  Stats: {self.stats}"
        ]
        return "\n".join(parts)