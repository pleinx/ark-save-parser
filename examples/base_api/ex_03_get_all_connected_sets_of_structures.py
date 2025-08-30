from pathlib import Path

from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.api import BaseApi


as_json = {}

if __name__ == '__main__':
    path = Path.cwd() / "Ragnarok_WP.ark" # or your local path to the save file
    save = AsaSave(path)
    bApi = BaseApi(save, ArkMap.RAGNAROK)

    bases = bApi.get_all(only_connected=True)
    nr_parsed = 0

    print(f"Found {len(bases)} bases")
    for i, base in enumerate(bases):
        location = None if base.keystone.location is None else base.keystone.location.as_map_coords(ArkMap.RAGNAROK)
        nr_of_structures = len(base.structures)
        if nr_of_structures == 1:
            name = base.structures[base.keystone.uuid].blueprint
        elif location is None:
            name = "base_" + str(i) + "_" + str(nr_of_structures)
        else:
            name = "base_" + str(location.lat) + "_" + str(location.long) + "_" + str(nr_of_structures)

        as_json[name] = {
            "owner": base.owner.serialize(),
            "nr_of_structures": nr_of_structures,
            "location": { "lat": location.lat, "lon": location.long } if location is not None else "Unknown",
        }

        nr_parsed += 1

        print(f"Parsed {nr_parsed}/{len(bases)} bases", end="\r")

    with open("all_bases_ragnarok.json", "w") as f:
        import json
        json.dump(as_json, f, indent=4)

    
    sorted_by_owner = {}

    
