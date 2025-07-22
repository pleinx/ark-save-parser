from arkparse.api.player_api import PlayerApi
from pathlib import Path
from arkparse.saves.asa_save import AsaSave
from arkparse.logging import ArkSaveLogger

save_path = Path.cwd() / "temp" / "pleinx" / "Aberration_WP.ark" # Adjust the path as needed
save = AsaSave(save_path)

player_api = PlayerApi(save)

for player in player_api.players:
    print(player)

for tribe in player_api.tribes:
    print(tribe)
    for p in player_api.tribe_to_player_map[tribe.tribe_id]:
        print(f"  - {p}")
    for idx, p_id in enumerate(tribe.member_ids):
        is_active = False
        for pl in player_api.tribe_to_player_map[tribe.tribe_id]:
            if pl.id_ == p_id:
                is_active = True
        if not is_active:
            print(f"  - {tribe.members[idx]}, id {p_id} (Inactive; not found in players)")
