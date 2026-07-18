import json
import math
import re
from pathlib import Path

from arkparse.enums import ArkMap
from arkparse.parsing.struct import ActorTransform, ArkVector


GENESIS_PIX_DINO_NAME_PATTERN = re.compile(r"^PIX[1-6]_(\d+(?:\.\d+)?)_(\d+(?:\.\d+)?)$")


def test_genesis_coordinates_match_pix_tamed_dino_references():
    output_path = Path(__file__).resolve().parents[4] / "output" / "gen1_a" / "TamedDinos.json"
    dinos = json.loads(output_path.read_text())["data"]
    reference_dinos = [
        (dino, name_match)
        for dino in dinos
        if (name_match := GENESIS_PIX_DINO_NAME_PATTERN.match(dino.get("name") or ""))
    ]

    assert len(reference_dinos) == 6

    for dino, name_match in reference_dinos:
        expected_lat = float(name_match.group(1))
        expected_lon = float(name_match.group(2))
        x, y, z = (float(value) for value in dino["ccc"].split())
        location = ActorTransform(vector=ArkVector(x=x, y=y, z=z))

        coords = location.as_map_coords(ArkMap.GENESIS)

        assert math.isclose(coords.lat, expected_lat, abs_tol=0.5)
        assert math.isclose(coords.long, expected_lon, abs_tol=0.5)
