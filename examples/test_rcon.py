from pathlib import Path
from arkparse.api.rcon_api import RconApi
from arkparse.classes.dinos import Dinos

rcon: RconApi = RconApi.from_config(Path.cwd().parent / "rcon_config.json")

print("Chat:")
for entry in rcon.get_chat():
    print(entry)

print("Game log:")
for entry in rcon.game_log:
    print(entry)

rcon.send_cmd(f"GetAllState {Dinos.cosmo.split('.')[-1]}")