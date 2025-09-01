# ASV JSON Export (Port)

### Coming from ASV (Ark Savegame Visualizer)?
This is a port of ASV’s JSON export. With these scripts you can generate the **same JSON output** that ASV produces, using Arkparse under the hood.  
The port is not yet complete and still has some **open TODOs**, but you’re welcome to use it and contribute.


### Exporting Structures
```cmd
py examples/asv_json_export/export_structures.py --savegame="temp/Ragnarok_WP/Ragnarok_WP.ark" --output="json_exports"
```

### Exporting Wild Dinos (tamables only)
```cmd
py examples/asv_json_export/export_wild_tamables.py --savegame="temp/Ragnarok_WP/Ragnarok_WP.ark" --output="json_exports"
```

### Exporting Tamed Dinos
```cmd
py examples/asv_json_export/export_tamed.py --savegame="temp/Ragnarok_WP/Ragnarok_WP.ark" --output="json_exports"
```

# Good2Know
The exporter will create an output folder like this `json_exports/{MAP_NAME}_Structures.json`.
You want to customize it? I'll add this soon!

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