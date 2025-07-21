from pathlib import Path
from typing import List, Optional

from arkparse.logging import ArkSaveLogger
from arkparse.saves.save_context import SaveContext

from .ark_object import ArkObject
from .ark_binary_parser import ArkBinaryParser
from .ark_property import ArkProperty

class ArkArchive:
    def __init__(self, file: Path):
        self.objects: List[ArkObject] = []
        

        save_context: SaveContext = SaveContext()
        data = ArkBinaryParser(file.read_bytes(), save_context)
        self.data = data
        ArkSaveLogger.set_file(data, "debug.bin")
        ArkSaveLogger.byte_buffer = data
        # ArkSaveLogger.open_hex_view(True)
        save_context.save_version = data.read_int()
        ArkSaveLogger.debug_log(f"Archive version: {save_context.save_version}")
        if save_context.save_version != 7:
            raise RuntimeError(f"Unsupported archive version {save_context.save_version} (only Unreal 5.5 / binary version 7 is supported)")
        extra1 = data.read_int()  # This is usually 0, but can be used for future extensions
        extra2 = data.read_int()
        ArkSaveLogger.file = str(file)

        count = data.read_int()
        for _ in range(count):
            self.objects.append(ArkObject.from_reader(data))

        ArkSaveLogger.debug_log(f"Read {len(self.objects)} objects from archive")

        for i, obj in enumerate(self.objects):
            ArkSaveLogger.enter_struct(obj.class_name.split(".")[-1])
            data.set_position(obj.properties_offset + 1)
            if ArkSaveLogger.enable_debug:
                print("\n")
            ArkSaveLogger.debug_log(f"Reading properties for object \'{obj.class_name}\' at {data.get_position()}")

            next_object_index = data.size()
            if i + 1 < len(self.objects):
                next_object_index = self.objects[i + 1].properties_offset
            
            obj.read_properties(data, ArkProperty, next_object_index)
            ArkSaveLogger.exit_struct()

    def get_all_objects_by_class(self, class_name: str) -> List[ArkObject]:
        return [obj for obj in self.objects if obj.class_name == class_name]

    def get_object_by_class(self, class_name: str) -> Optional[ArkObject]:
        return next((obj for obj in self.objects if obj.class_name == class_name), None)

    def get_object_by_uuid(self, uuid_: str) -> Optional[ArkObject]:
        return next((obj for obj in self.objects if obj.uuid == uuid_), None)

    def get_object_by_index(self, index: int) -> ArkObject:
        return self.objects[index]
