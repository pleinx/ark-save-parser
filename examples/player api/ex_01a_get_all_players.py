from arkparse.ftp.ark_ftp_client import ArkMap
from arkparse.api.player_api import PlayerApi

player_api = PlayerApi('../../ftp_config.json', ArkMap.ABERRATION)

for player in player_api.players:
    print(player)