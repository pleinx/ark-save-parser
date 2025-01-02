from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.api.player_api import PlayerApi
from arkparse.object_model.misc.inventory import Inventory

player_api = PlayerApi('../../ftp_config.json', ArkMap.ABERRATION)
save = AsaSave(contents=ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file())

for player in player_api.players:   
    inventory: Inventory = player_api.get_player_inventory(player, save)
    print(player)
    print(f"{player.name}'s inventory:")
    print(inventory)
    print("\n")