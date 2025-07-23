from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, TYPE_CHECKING
from contextlib import contextmanager

from arkparse.logging import ArkSaveLogger

from arkparse.parsing.struct.ark_color import ArkColor
from arkparse.parsing.struct.ark_int_point import ArkIntPoint
from arkparse.parsing.struct.ark_linear_color import ArkLinearColor
from arkparse.parsing.struct.ark_quat import ArkQuat
from arkparse.parsing.struct.ark_rotator import ArkRotator
from arkparse.parsing.struct.ark_vector import ArkVector
from arkparse.parsing.struct.ark_unique_net_id_repl import ArkUniqueNetIdRepl
from arkparse.parsing.struct.ark_vector_bool_pair import ArkVectorBoolPair
from arkparse.parsing.struct.ark_tracked_actor_id_category_pair_with_bool import (
    ArkTrackedActorIdCategoryPairWithBool,
)
from arkparse.parsing.struct.ark_my_persistent_buff_datas import ArkMyPersistentBuffDatas
from arkparse.parsing.struct.ark_item_net_id import ArkItemNetId
from arkparse.parsing.struct.object_reference import ObjectReference
from arkparse.parsing.struct.ark_struct_type import ArkStructType
from arkparse.parsing.struct.ark_dino_ancestor_entry import ArkDinoAncestorEntry
from arkparse.parsing.struct.ark_custom_item_data import ArkCustomItemData

from arkparse.parsing.ark_property_container import ArkPropertyContainer
from arkparse.parsing.ark_set import ArkSet

from .ark_value_type import ArkValueType
from ..enums.ark_enum import ArkEnumValue

if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser

T = TypeVar("T")

# -------------------------------------------------------------------------------------------------
# Logging helpers
# -------------------------------------------------------------------------------------------------

@contextmanager
def log_block(title: str):
    ArkSaveLogger.enter_struct(title)
    try:
        yield
    finally:
        ArkSaveLogger.exit_struct()


def log_property_read(key: str, vtype: ArkValueType, start_pos: int, data_size: int, value: Any, position: int) -> None:
    ArkSaveLogger.debug_log(
        f"[property read: key={key}; type={vtype}; bin_pos={start_pos}; bin_size={data_size}; value={value}; index_pos={position}]"
    )


# -------------------------------------------------------------------------------------------------
# Lookup tables
# -------------------------------------------------------------------------------------------------

# Map ArkStructType enum to constructors. Some need data_size, so we wrap with lambdas of (bb, ds)
_STRUCT_READERS: Dict[ArkStructType, Callable[["ArkBinaryParser", int], Any]] = {
    ArkStructType.Color: lambda bb, ds: ArkColor(bb),
    ArkStructType.LinearColor: lambda bb, ds: ArkLinearColor(bb),
    ArkStructType.Quat: lambda bb, ds: ArkQuat(bb),
    ArkStructType.Rotator: lambda bb, ds: ArkRotator(bb),
    ArkStructType.Vector: lambda bb, ds: ArkVector(bb),
    ArkStructType.UniqueNetIdRepl: lambda bb, ds: ArkUniqueNetIdRepl(bb),
    ArkStructType.VectorBoolPair: lambda bb, ds: ArkVectorBoolPair(bb),
    ArkStructType.ArkTrackedActorIdCategoryPairWithBool: lambda bb, ds: ArkTrackedActorIdCategoryPairWithBool(bb),
    ArkStructType.MyPersistentBuffDatas: lambda bb, ds: ArkMyPersistentBuffDatas(bb, ds),
    ArkStructType.ItemNetId: lambda bb, ds: ArkItemNetId(bb),
    ArkStructType.ArkDinoAncestor: lambda bb, ds: ArkDinoAncestorEntry(bb),
    ArkStructType.ArkIntPoint: lambda bb, ds: ArkIntPoint(bb),
    ArkStructType.ArkCustomItemData: lambda bb, ds: ArkCustomItemData(bb),
}

# Flags driving how a primitive value is read
class _Spec:
    __slots__ = ("needs_unknown", "needs_pos_flag", "reader")

    def __init__(self, needs_unknown: bool, needs_pos_flag: bool, reader: Callable[["ArkBinaryParser"], Any]):
        self.needs_unknown = needs_unknown
        self.needs_pos_flag = needs_pos_flag
        self.reader = reader


_SIMPLE_SPECS: Dict[ArkValueType, _Spec] = {
    ArkValueType.Boolean: _Spec(False, False, lambda bb: bb.read_byte() != 0),
    ArkValueType.Int: _Spec(True, False, lambda bb: bb.read_int()),
    ArkValueType.Double: _Spec(True, False, lambda bb: bb.read_double()),
    ArkValueType.UInt32: _Spec(True, False, lambda bb: bb.read_uint32()),
    ArkValueType.UInt64: _Spec(True, False, lambda bb: bb.read_uint64()),
    ArkValueType.Int64: _Spec(True, False, lambda bb: bb.read_int64()),
    ArkValueType.String: _Spec(True, False, lambda bb: bb.read_string()),
    ArkValueType.SoftObject: _Spec(True, False, lambda bb: ArkProperty.read_soft_object_property_value(bb)),

    ArkValueType.Name: _Spec(False, True, lambda bb: bb.read_name()),
    ArkValueType.Float: _Spec(False, True, lambda bb: bb.read_float()),
    ArkValueType.Int8: _Spec(False, True, lambda bb: bb.read_byte()),
    ArkValueType.Object: _Spec(False, True, lambda bb: ObjectReference(bb)),
    ArkValueType.UInt16: _Spec(False, True, lambda bb: bb.read_uint16()),
    ArkValueType.Int16: _Spec(False, True, lambda bb: bb.read_short()),
}

_LOGGABLE_COMPLEX = {ArkValueType.Struct, ArkValueType.Array, ArkValueType.Map, ArkValueType.Set}


# -------------------------------------------------------------------------------------------------
# Dataclass
# -------------------------------------------------------------------------------------------------
@dataclass
class ArkProperty:
    name: str
    type: str
    value: Any
    position: int = field(default=0)
    unknown_byte: Optional[int] = field(default=None, repr=False)

    nr_of_bytes: int = field(default=0, init=False)
    name_position: int = field(default=0, init=False)
    value_position: int = field(default=0, init=False)
    bytes: Optional[bytes] = field(default=None, init=False, repr=False)

    def __init__(self, name: str, type: str, position: int, unknown_byte: int, value: T):
        # Keep ctor to match the original signature/behavior
        self.name = name
        self.type = type
        self.position = position
        self.unknown_byte = unknown_byte
        self.value = value
        self.nr_of_bytes = 0
        self.name_position = 0
        self.value_position = 0
        self.bytes = None

    # ---------------------------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def read_property(byte_buffer: "ArkBinaryParser", in_array: bool = False) -> Optional["ArkProperty"]:
        name_position = byte_buffer.get_position()
        value_position = 0
        key = byte_buffer.read_name()

        if key is None or key == "None":
            ArkSaveLogger.debug_log("Exiting struct (None marker)")
            ArkSaveLogger.exit_struct()
            return None

        value_type = byte_buffer.read_value_type_by_name()
        data_size = byte_buffer.read_int()
        position = byte_buffer.read_int()
        start_data_position = byte_buffer.get_position()

        if value_type in _LOGGABLE_COMPLEX:
            ArkSaveLogger.debug_log(
                f"[prop={key};  type={value_type}; bin_pos={start_data_position}; size={data_size}; index_pos={position}]"
            )

        # Dispatch simple/complex
        if value_type in _SIMPLE_SPECS:
            prop, value_position = ArkProperty._read_simple_property(key, value_type, position, byte_buffer)
        elif value_type == ArkValueType.Byte:
            prop, value_position = ArkProperty._read_byte_property(key, position, data_size, byte_buffer)
        elif value_type == ArkValueType.Struct:
            byte_buffer.set_position(byte_buffer.get_position() - 4)  # V14 fix
            struct_type = byte_buffer.read_name()
            val, value_position = ArkProperty.read_struct_property(byte_buffer, data_size, struct_type, in_array)
            prop = ArkProperty(key, value_type.name, position, 0, val)
        elif value_type == ArkValueType.Array:
            prop = ArkProperty.read_array_property(key, value_type.name, position, byte_buffer, data_size)
        elif value_type == ArkValueType.Map:
            byte_buffer.set_position(byte_buffer.get_position() - 4)
            prop = ArkProperty.read_map_property(key, value_type.name, position, byte_buffer, data_size)
        elif value_type == ArkValueType.Set:
            byte_buffer.set_position(byte_buffer.get_position() - 4)
            prop = ArkProperty.read_set_property(key, value_type.name, position, byte_buffer, data_size)
        else:
            print(
                f"Unsupported property type {value_type} with data size {data_size} at position {start_data_position}"
            )
            prop = None

        if value_type not in _LOGGABLE_COMPLEX and prop is not None:
            log_property_read(key, value_type, start_data_position, data_size, prop.value, position)

        if prop is not None:
            prop.nr_of_bytes = data_size
            prop.name_position = name_position
            prop.value_position = value_position
            prop.bytes = byte_buffer.byte_buffer[name_position:byte_buffer.get_position()]

        return prop

    # ---------------------------------------------------------------------------------------------
    # Simple/primitive readers
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def _read_simple_property(key: str, vtype: ArkValueType, position: int, bb: "ArkBinaryParser") -> Tuple["ArkProperty", int]:
        spec = _SIMPLE_SPECS[vtype]

        unknown = bb.read_byte() if spec.needs_unknown else 0
        meta_flag = unknown
        if spec.needs_pos_flag:
            is_pos = bb.read_byte() == 1
            position = bb.read_int() if is_pos else 0
            meta_flag = is_pos  # preserve original semantics of unknown_byte field for these types
        value_position = bb.get_position()
        value = spec.reader(bb)

        return ArkProperty(key, vtype.name, position, meta_flag, value), value_position

    @staticmethod
    def _read_byte_property(key: str, position: int, data_size: int, bb: "ArkBinaryParser") -> Tuple["ArkProperty", int]:
        pre_read_pos = bb.get_position()
        is_enum = data_size != 0  # original heuristic

        if not is_enum:
            is_position = bb.read_byte() == 1  # or data size??? preserved behavior
            position = bb.read_int() if is_position else 0
            value_position = bb.get_position()
            byte_val = bb.read_unsigned_byte()
            return ArkProperty(key, ArkValueType.Byte.name, position, 0, byte_val), value_position

        # Enum path
        bb.set_position(pre_read_pos - 4)
        enum_type = bb.read_name()  # unused but kept
        _size = bb.read_int()
        _enum_bp = bb.read_name()  # unused but kept
        bb.validate_uint32(0)
        _enum_byte_size = bb.read_byte()
        bb.validate_uint32(0)
        enum_name = bb.read_name()
        ArkSaveLogger.debug_log(f"[ENUM: key={key}; value={ArkEnumValue(enum_name)}; start_pos={pre_read_pos}]")
        value_position = bb.get_position()
        return ArkProperty(key, ArkValueType.Enum, position, data_size, ArkEnumValue(enum_name)), value_position

    # ---------------------------------------------------------------------------------------------
    # Map/Set/Array readers
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def read_map_property(key: str, value_type_name: str, position: int, bb: "ArkBinaryParser", data_size: int) -> "ArkProperty":
        key_type = bb.read_value_type_by_name()
        bb.validate_uint32(0)
        value_type = bb.read_value_type_by_name()
        count = bb.read_int()

        map_name = bb.read_name()
        data_size, position, read_pos = ArkProperty.__read_struct_header(bb, 0, in_array=True)
        start_of_data = bb.get_position() - 4 if read_pos else 0
        _ = bb.read_int()  # seems to be 1

        entries: List[ArkProperty] = []
        for _ in range(count):
            if value_type == ArkValueType.Struct:
                entries.append(ArkProperty.read_struct_map(key_type, bb, map_name))
            else:
                ArkSaveLogger.open_hex_view()
                raise ValueError(f"Unsupported map value type {value_type}")

        ArkProperty._fixup_if_left(bb, start_of_data, data_size, "Map")

        prop = ArkProperty(key, value_type_name, position, 0, ArkPropertyContainer(entries))
        
        return prop

    @staticmethod
    def read_struct_map(key_type: ArkValueType, bb: "ArkBinaryParser", map_name: str) -> "ArkProperty":
        props: List[ArkProperty] = []
        key_name = ArkProperty.read_property_value(key_type, bb)
        with log_block(f"Map({key_name}:{map_name})"):
            while bb.has_more():
                p = ArkProperty.read_property(bb)
                if p is None:
                    break
                props.append(p)
        return ArkProperty(key_name, "MapProperty", 0, 0, ArkPropertyContainer(props))

    @staticmethod
    def read_set_property(key: str, value_type_name: str, position: int, bb: "ArkBinaryParser", data_size: int) -> "ArkProperty":
        value_type = bb.read_value_type_by_name()
        bb.validate_uint32(0)
        data_size = bb.read_int()
        bb.validate_byte(0)
        start_of_data = bb.get_position()
        bb.validate_uint32(0)
        count = bb.read_int()

        with log_block(f"Set({value_type})"):
            values = [ArkProperty.read_property_value(value_type, bb) for _ in range(count)]

        if start_of_data + data_size != bb.get_position():
            print("Set read incorrectly, bytes left to read, expected:", start_of_data + data_size - bb.get_position())

        ArkSaveLogger.debug_log(f"Read set property {key} with {count} values of type {value_type_name}")
        ArkSaveLogger.debug_log(f"Set values: {values}")

        prop = ArkProperty(key, value_type_name, position, 0, ArkSet(value_type, values))
    
        return prop

    @staticmethod
    def read_array_property(key: str, type_: str, position: int, bb: "ArkBinaryParser", data_size: int) -> "ArkProperty":
        # V14 no position in array
        bb.set_position(bb.get_position() - 4)
        array_type = bb.read_name()
        array_items = data_size
        _array_type_int = bb.read_int()
        array_length = None

        if array_type != "StructProperty":
            data_size = bb.read_uint32()
            end_of_struct = bb.read_byte()
            data_start_position = bb.get_position()
            array_length = bb.read_uint32()
        else:
            end_of_struct = 0  # not used, keep for signature
            data_start_position = 0

        start_values_pos = bb.get_position()

        if array_type == "StructProperty":
            array_content_type = bb.read_name()
            data_size, position, read_pos = ArkProperty.__read_struct_header(bb, position, in_array=True)
            data_start_position = bb.get_position() - (4 if read_pos else 0)

            with log_block(f"Arr({array_content_type})"):
                ArkSaveLogger.debug_log(
                    f"[STRUCT ARRAY: key='none'; nr_of_value={array_items}; type={array_content_type}; bin_length={data_size}]"
                )
                struct_array = [
                    ArkProperty.read_struct_property(bb, data_size, array_content_type, True)
                    for _ in range(array_items)
                ]

            prop = ArkProperty(key, type_, position, 0, struct_array)
            if bb.position != data_start_position + data_size:
                ArkSaveLogger.warning_log(
                    f"WARNING: Array read incorrectly, bytes left to read: {data_start_position + data_size - bb.position}"
                )
                ArkSaveLogger.warning_log(f"Skipping to the end of the struct, type: {array_content_type}")
                bb.set_position(data_start_position + data_size)

            return prop

        # Value array branch
        with log_block(f"Arr({array_type})"):
            ArkSaveLogger.debug_log(
                f"[VALUE ARRAY: key={key}; nr_of_values={array_length}; type={array_type}]"
            )

            if key == "MyPersistentBuffDatas":
                value, _ = ArkProperty.read_struct_property(bb, array_length, key, True)
                prop = ArkProperty(key, "Struct", position, 0x00, value)
            else:
                values: List[Any] = []
                for _ in range(array_length):
                    # Preserve original odd branch
                    if bb.read_uint32 == 0x09AD2622:  # pragma: no cover
                        values.append(bb.read_name())
                    else:
                        values.append(ArkProperty.read_property_value(ArkValueType.from_name(array_type), bb))

                if array_type != "ByteProperty":
                    for i, v in enumerate(values):
                        ArkSaveLogger.debug_log(f"value {i}: {v}")
                else:
                    ArkSaveLogger.debug_log(f"Array value: {values}")

                prop = ArkProperty(key, type_, position, end_of_struct, values)

        ArkSaveLogger.debug_log(f"============ END Arr({array_type}) ============")
        
        return prop

    # ---------------------------------------------------------------------------------------------
    # Struct reading
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def __read_struct_header(bb: "ArkBinaryParser", position: int = 0, in_array: bool = False) -> Tuple[int, int, bool]:
        bb.validate_uint32(1)  # V14 marker
        _new_name = bb.read_name()
        bb.validate_uint32(0)
        data_size = bb.read_uint32()
        size_byte = bb.read_byte()  # V14 unknown byte

        read_pos = (size_byte not in (0, 8)) or (in_array and size_byte == 0)
        if read_pos:
            position = bb.read_uint32()

        return data_size, position, read_pos

    @staticmethod
    def read_struct_property(bb: "ArkBinaryParser", data_size: int, struct_type: str, in_array: bool) -> Any:
        ArkSaveLogger.debug_log(f"Reading struct property {struct_type} with data size {data_size}")

        if not in_array:
            with log_block(f"S({struct_type})"):
                data_size, position, _ = ArkProperty.__read_struct_header(bb)
                value_position = bb.get_position()
                return ArkProperty._read_struct_body(bb, data_size, struct_type, in_array), value_position
        else:
            value_position = bb.get_position()
            return ArkProperty._read_struct_body(bb, data_size, struct_type, in_array), value_position

    @staticmethod
    def _read_struct_body(bb: "ArkBinaryParser", data_size: int, struct_type: str, in_array: bool) -> Any:
        ark_struct_type = ArkStructType.from_type_name(struct_type)

        if ark_struct_type or in_array:
            if data_size <= 4:
                return None
            if ark_struct_type in _STRUCT_READERS:
                return _STRUCT_READERS[ark_struct_type](bb, data_size)
            if ark_struct_type is None:
                return None
            if in_array:
                if bb.peek_name() == "None":
                    return bb.read_name()
                ArkSaveLogger.enable_debug = True
                ArkSaveLogger.open_hex_view(True)
                raise ValueError(f"Unsupported struct type {ark_struct_type}")

        # Fallback: struct as property list
        position = bb.get_position()
        props = ArkProperty.read_struct_properties(bb)
        if bb.get_position() != position + data_size and not in_array:
            if not ArkSaveLogger.suppress_warnings:
                print("WARNING: Struct reading position mismatch for type", struct_type)
                print(
                    f"StructType: {struct_type}, DataSize: {data_size}, Position: {position}, CurrentPosition: {bb.get_position()}"
                )
            bb.set_position(position + data_size)
        return props

    @staticmethod
    def read_struct_properties(bb: "ArkBinaryParser") -> ArkPropertyContainer:
        props: List[ArkProperty] = []
        struct_property = ArkProperty.read_property(bb)
        if struct_property is not None:
            ArkSaveLogger.debug_log(
                f"Struct properties: {struct_property.name} {struct_property.type} {struct_property.value}"
            )
        while struct_property:
            props.append(struct_property)
            if bb.has_more():
                struct_property = ArkProperty.read_property(bb)
                if struct_property is not None:
                    ArkSaveLogger.debug_log(
                        f"Struct properties: {struct_property.name} {struct_property.type} {struct_property.value}"
                    )
            else:
                break

        ArkSaveLogger.debug_log(f"Read {len(props)} struct properties")
        return ArkPropertyContainer(props)

    # ---------------------------------------------------------------------------------------------
    # Misc helpers
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def read_property_value(value_type: ArkValueType, bb: "ArkBinaryParser") -> Any:
        if value_type in _SIMPLE_SPECS:
            return _SIMPLE_SPECS[value_type].reader(bb)
        if value_type == ArkValueType.Byte:
            return bb.read_unsigned_byte()
        if value_type == ArkValueType.Struct:
            prop, _ = ArkProperty.read_struct_property(bb, bb.read_int(), True)
            return prop
        raise RuntimeError(f"Cannot read value type: {value_type} at position {bb.get_position()}")

    @staticmethod
    def read_soft_object_property_value(bb: "ArkBinaryParser") -> str:
        with log_block("SfO"):
            obj_name = bb.read_name()
            bb.validate_bytes_as_string("00 00 00 00", 4)
            ArkSaveLogger.debug_log(f"Read soft object property {obj_name}")
            return obj_name

    @staticmethod
    def _fixup_if_left(bb: "ArkBinaryParser", start: int, size: int, label: str) -> None:
        if bb.get_position() != start + size:
            remaining = bb.read_bytes(start + size - bb.get_position())
            ArkSaveLogger.debug_log(f"{label} read incorrectly, bytes left to read:", remaining)
