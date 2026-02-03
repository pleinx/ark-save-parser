from pathlib import Path
from arkparse.parsing.ark_archive import ArkArchive
from arkparse.logging import ArkSaveLogger
from arkparse.parsing.ark_property_container import set_print_depth
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.dinos import Dino, DinoStats

# ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ALL, True)

def get_files(path: Path) -> list[Path]:
    return [f for f in path.iterdir() if (f.is_file() and not f.name.endswith(".py"))]

files = get_files(Path().cwd())
for file in files:
    if file.name.endswith(".status"):
        continue
    ArkSaveLogger.info_log(f"Found file: {file.name}")
    bytes_ = (Path().cwd() / file.name).read_bytes()
    data_parser = ArkBinaryParser(bytes_)
    # arch = ArkArchive(bytes_, from_store=False)
    # print(arch)

    unknown_sequence1 = data_parser.read_bytes(12)
    dino_uuid = data_parser.read_uuid()
    class_name = data_parser.read_string()
    data_parser.validate_uint32(0)
    nr_of_names = data_parser.read_uint32()
    names = []
    for _ in range(nr_of_names):
        names.append(data_parser.read_string())
    data_parser.validate_uint64(0)
    data_parser.validate_uint32(1)
    uuid1 = data_parser.read_uuid()
    uuid2 = data_parser.read_uuid()
    uuid3 = data_parser.read_uuid()

    print(f"\n=== Parsed data for file: {file.name} ===")
    print("Unknown sequence (12 bytes):", ", ".join(f"{b:02x}" for b in unknown_sequence1))
    print(f"File: {file.name}")
    print(f"Class name: {class_name}")
    print(f"Names: {names}")
    print(f"UUIDs: {dino_uuid}, {uuid1}, {uuid2}, {uuid3}")

    if dino_uuid != uuid3:
        ArkSaveLogger.error_log(f"UUID mismatch: {dino_uuid} != {uuid3}")

    status_component_class = data_parser.read_name()
    data_parser.validate_uint32(0)
    nr_of_names = data_parser.read_uint32()
    status_names = []
    for _ in range(nr_of_names):
        status_names.append(data_parser.read_string())

    unknown_sequence = data_parser.read_bytes(21)
    
    print(f"Status component class: {status_component_class}")
    print(f"Status names: {status_names}")
    print("Unknown sequence (21 bytes):", ", ".join(f"{b:02x}" for b in unknown_sequence))

    dino_uuid_positions = [pos for pos in data_parser.find_byte_sequence(dino_uuid.bytes)]
    print(f"UUID1 found at positions: {dino_uuid_positions}, hex: {[hex(pos) for pos in dino_uuid_positions]}")
    
    dino_data = data_parser.byte_buffer[data_parser.get_position(): dino_uuid_positions[2] + 1]
    dino_obj = ArkGameObject(uuid=dino_uuid, blueprint=class_name, binary_reader=ArkBinaryParser(dino_data), no_header=True)

    data_parser.set_position(data_parser.size()-22)
    status_uud = data_parser.read_uuid()

    status_uuid_positions = [pos for pos in data_parser.find_byte_sequence(status_uud.bytes)]
    print(f"Status UUID found at positions: {status_uuid_positions}, hex: {[hex(pos) for pos in status_uuid_positions]}")

    data_parser.set_position(dino_uuid_positions[2] + 22)
    status_data = data_parser.byte_buffer[data_parser.get_position():]
    status_obj = ArkGameObject(uuid=dino_uuid, blueprint=status_component_class, binary_reader=ArkBinaryParser(status_data), no_header=True)

    dino = Dino.from_object(dino_obj, status_obj)

    print("\nDino data:")
    print(dino)

    print("\nDino stats:")
    print(dino.stats.to_string_all())