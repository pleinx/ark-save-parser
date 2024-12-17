from typing import Dict
from uuid import UUID
from pathlib import Path
import json

import arkparse.parsing.struct as structs
from arkparse.object_model.structures import Structure
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.object_model.misc.object_owner import ObjectOwner

class Base:
    structures: Dict[UUID, Structure]
    location: ActorTransform
    keystone: Structure
    owner: ObjectOwner

    def __determine_location(self):
        average_x = 0
        average_y = 0
        average_z = 0

        for _, structure in self.structures.items():
            average_x += structure.location.x
            average_y += structure.location.y
            average_z += structure.location.z

        average_x /= len(self.structures)
        average_y /= len(self.structures)
        average_z /= len(self.structures)

        self.location = structs.ActorTransform(vector=structs.ArkVector(x=average_x, y=average_y, z=average_z))

    def __init__(self, keystone: UUID = None, structures: Dict[UUID, Structure] = None):
        self.structures = structures
        if self.structures is not None:
            self.__determine_location()
        self.set_keystone(keystone)

    def __serialize(self):
        return {
            "location": self.location.as_json(),
            "keystone": str(self.keystone.object.uuid),
        }

    def set_keystone(self, keystone: UUID):
        if keystone is not None:
            self.keystone = self.structures[keystone]
            self.location = self.keystone.location
            self.owner = self.keystone.owner
        else:
            self.keystone = None
            self.owner = None

    def move_to(self, new_location: ActorTransform):
        offset_x = new_location.x - self.location.x
        offset_y = new_location.y - self.location.y
        offset_z = new_location.z - self.location.z

        for _, structure in self.structures.items():
            structure.location.update(structure.location.x + offset_x, structure.location.y + offset_y, structure.location.z + offset_z)

    def set_owner(self, new_owner: ObjectOwner):
        for _, structure in self.structures.items():
            structure.owner.replace_self_with(new_owner, structure.binary)

    def store_binary(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "base.json", "w") as f:
            json.dump(self.__serialize(), f, indent=4)
        for _, structure in self.structures.items():
            structure.store_binary(path)

    def import_from_binaries(self, path: Path):
        pass
