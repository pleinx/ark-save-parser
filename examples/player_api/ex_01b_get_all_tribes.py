from arkparse.ftp.ark_ftp_client import ArkMap
from arkparse.api.player_api import PlayerApi

player_api = PlayerApi('../../ftp_config.json', ArkMap.ABERRATION)

for tribe in player_api.tribes:
    print(tribe)
    for p in player_api.tribe_to_player_map[tribe.tribe_id]:
        print(f"  - {p}")