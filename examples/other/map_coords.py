from arkparse.parsing.struct.actor_transform import MapCoordinateParameters

map_coords = {
    "SCORCHEDEARTH_WP": {
        "x": [-213606, -12667, 68924, 33801, 272823],
        "y": [5060, -86442, 73659, 358272, -309144],
        "lat": [50.6, 39, 59.3, 95.5, 10.7],
        "long": [22.9, 48.4, 58.7, 54.3, 84.6]
    },
    "ASTRAEOS_WP": {
        "x": [213208, 543179, 737106, 418669, 90740],
        "y": [-475816, -626802, -155344, -146668, -124852],
        "lat": [20.3, 10.8, 40.3, 40.8, 42.2],
        "long": [63.3, 83.9, 96.1, 76.2, 55.7]
    },
    "THE_CENTER_WP": {
        "x": [194543, 59715, -81580, -309519, -168058],
        "y": [-104839, 48224, 432401, 650099, -79835],
        "lat": [22.4, 37.2, 74.2, 95.2, 24.8],
        "long": [69.3, 56.3, 42.7, 20.7, 34.3]
    },
    "THE_ISLAND_WP": {
        "x": [178386, 66518, -286731, -94886, 107530],
        "y": [71381, -98198, -141238, -283358, -154017],
        "lat": [60.4, 35.7, 29.4, 8.7, 27.5],
        "long": [76, 59.7, 8.2, 36.2, 65.7]
    }
}

for map_name, data in map_coords.items():
    x = data["x"]
    y = data["y"]
    lat = data["lat"]
    long = data["long"]

    latitude_scale, latitude_shift, longitude_scale, longitude_shift = MapCoordinateParameters.fit_transform_params(x, y, lat, long)

    print(f"MapName: {map_name}")
    print(f"Latitude Scale: {latitude_scale}, Latitude Shift: {latitude_shift}")
    print(f"Longitude Scale: {longitude_scale}, Longitude Shift: {longitude_shift}")
