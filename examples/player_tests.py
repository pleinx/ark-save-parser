from pathlib import Path

from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api.player_api import PlayerApi

from arkparse.logging import ArkSaveLogger
# ArkSaveLogger.enable_debug = True
# ArkSaveLogger.temp_file_path = Path.cwd()

ftp_client = ArkFtpClient.from_config('../ftp_config.json', FtpArkMap.ABERRATION)
player_api = PlayerApi('../ftp_config.json', FtpArkMap.ABERRATION)

print(f"Total deaths: {player_api.get_deaths()}")
print(f"Total experience: {player_api.get_xp()}")
print(f"Combined level: {player_api.get_level()}")
print(f"Total players: {len(player_api.players)}")
print(f"Total tribes: {len(player_api.tribes)}")

for player in player_api.players:
    print(f"Player: {player.player_data.name} - Level: {player.player_data.stats.level} - Deaths: {player.player_data.nr_of_deaths}")

p, v = player_api.get_player_with(player_api.Stat.LEVEL, player_api.StatType.HIGHEST)
print(f"Highest level player: {p.player_data.name} ({v})")

p, v = player_api.get_player_with(player_api.Stat.DEATHS, player_api.StatType.HIGHEST)
print(f"Most deaths: {p.player_data.name} ({v})")
