from pathlib import Path

from src.arkparse import AsaSave
from src.arkparse.api.json_api import JsonApi

save_path = Path.cwd() / "Ragnarok_WP.ark" # replace with path to your save file
save = AsaSave(save_path) # loads save file
json_api = JsonApi(save) # initializes the JSON API

json_api.export_items() # exports items to JSON
