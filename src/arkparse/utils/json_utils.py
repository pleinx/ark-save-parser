import json
from pathlib import Path
from typing import Any

from uuid import UUID
from arkparse.struct.ark_struct_type import ArkStructType

class JsonUtils:
    @staticmethod
    def write_json_to_file(obj, file_path, indent=4):
        def custom_serializer(o):
            if isinstance(o, UUID):
                return str(o)  # Convert UUID to string
            elif isinstance(o, ArkStructType):
                return o.to_dict()  # Custom to_dict method for ArkStructType
            elif hasattr(o, "__dict__"):
                return o.__dict__  # Default to dict for other objects with __dict__
            else:
                return str(o)  # Fallback for any other type
            
        # Ensure the directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write the JSON to the file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=indent, default=custom_serializer, ensure_ascii=False)

    @staticmethod
    def to_json_string(obj: Any, indent: int = 4) -> str:
        """
        Returns the JSON string representation of `obj`.
        """
        try:
            return json.dumps(obj, indent=indent, default=lambda o: o.__dict__, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise RuntimeError("Error converting object to JSON string") from e
