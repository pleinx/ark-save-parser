from arkparse.ftp.ark_ftp_client import FtpArkMap
from arkparse.api.player_api import PlayerApi

player_api = PlayerApi('../ftp_config.json', FtpArkMap.ABERRATION)

for tribe in player_api.tribes:
    print(tribe.tribe_data)