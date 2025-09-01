# ASV JSON Export (Port)

### Coming from ASV (Ark Savegame Visualizer)?
This is a port of ASV’s JSON export. With these scripts you can generate the **same JSON output** that ASV produces, using Arkparse under the hood.  
The port is not yet complete and still has some **open TODOs**, but you’re welcome to use it and contribute.


### Exporting Structures
```cmd
py examples/asv_json_export/export_structures.py --serverkey="ragnarok_1" --savegame="temp/Ragnarok_WP/Ragnarok_WP.ark" --output="json_exports"
```

### Exporting Wild Dinos (tamables only)
```cmd
py examples/asv_json_export/export_wild.py --serverkey="ragnarok_1" --savegame="temp/Ragnarok_WP/Ragnarok_WP.ark" --output="json_exports"
```

### Exporting Tamed Dinos
```cmd
py examples/asv_json_export/export_tamed.py --serverkey="ragnarok_1" --savegame="temp/Ragnarok_WP/Ragnarok_WP.ark" --output="json_exports"
```

# ServerKey Parameter
This is new. Some clusters have multiple server instances of a map. If you use this:
```cmd
py examples/asv_json_export/export_tamed.py --serverkey="ragnarok_1" --savegame="temp/Ragnarok1/Ragnarok_WP/Ragnarok_WP.ark" --output="json_exports"
```
The output will be here `json_export/ragnarok_1/Tamed.json`

# Open Todos
### Structures
- Missing Inventory

### Tames
- Missing properties: 
  - isMating
  - isNeutered
  - isClone
  - traits
  - inventory

### Wild
- It contains only tamables yet, because the rest was not usable for me. If you really need also the other wild dinos, let me know :)