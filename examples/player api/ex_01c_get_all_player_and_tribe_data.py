from arkparse.api.player_api import PlayerApi
from pathlib import Path
from arkparse.saves.asa_save import AsaSave

save_path = Path.cwd() / "temp" / "Aberration_WP.ark" # Adjust the path as needed
save = AsaSave(save_path)

player_api = PlayerApi(save)

for player in player_api.players:
    print(player)

for tribe in player_api.tribes:
    print(tribe)
    for p in player_api.tribe_to_player_map[tribe.tribe_id]:
        print(f"  - {p}")