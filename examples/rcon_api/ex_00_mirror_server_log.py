import os
import time

from arkparse.api import RconApi

host = os.getenv("RCON_HOST")
port = int(os.getenv("RCON_PRT"))
password = os.getenv("RCON_PW")

print(f"Connecting to RCON at {host}:{port}...")
rcon = RconApi(host, port, password)
handle = rcon.subscribe()

input("Subscribed to server log. Press Enter to start mirroring...")
print("Mirroring server log. Press Ctrl-C to stop.")
while True:
    entries = rcon.get_new_entries(handle)
    if len(entries) > 0:
        for entry in entries:
            print(entry)
    time.sleep(0.3)