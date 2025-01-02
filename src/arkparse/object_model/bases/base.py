from typing import Dict
from uuid import UUID, uuid4
from pathlib import Path
import json
from importlib.resources import files

from arkparse import Classes
from arkparse import AsaSave
import arkparse.parsing.struct as structs
from arkparse.object_model.stackables import Ammo, Resource
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.parsing import ArkBinaryParser

class Base:
    structures: Dict[UUID, Structure]
    location: ActorTransform
    keystone: Structure
    owner: ObjectOwner
    nr_of_turrets: int

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
        self.__count_turrets()

    def __serialize(self):
        return {
            "location": self.location.as_json(),
            "keystone": str(self.keystone.object.uuid),
            "owner": self.owner.serialize(),
            "nr_of_turrets": self.nr_of_turrets,
        }
    
    def __count_turrets(self):
        count = 0
        for _, structure in self.structures.items():
            if structure.object.blueprint in Classes.structures.placed.turrets.all_bps:
                count += 1
        self.nr_of_turrets = count

    def set_keystone(self, keystone: UUID):
        if keystone is not None:
            self.keystone = self.structures[keystone]
            self.location = self.keystone.location
            self.owner = self.keystone.owner
        else:
            self.keystone = None
            self.owner = None

    def move_to(self, new_location: ActorTransform, save: AsaSave = None):
        offset_x = new_location.x - self.location.x
        offset_y = new_location.y - self.location.y
        offset_z = new_location.z - self.location.z

        for _, structure in self.structures.items():
            structure.location.update(structure.location.x + offset_x, structure.location.y + offset_y, structure.location.z + offset_z)

        if save is not None:
            for _, structure in self.structures.items():
                save.modify_actor_transform(structure.object.uuid, structure.location.to_bytes())

    def set_owner(self, new_owner: ObjectOwner, save: AsaSave):
        for _, structure in self.structures.items():
            structure.owner.replace_self_with(new_owner, structure.binary)
            save.modify_game_obj(structure.object.uuid, structure.binary.byte_buffer)

    def store_binary(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "base.json", "w") as f:
            json.dump(self.__serialize(), f, indent=4)
        for _, structure in self.structures.items():
            structure.store_binary(path)

    def pad_turret_ammo(self, nr_of_stacks: int, save: AsaSave):
        
        for inv_key, structure in self.structures.items():
            if structure.object.blueprint in Classes.structures.placed.turrets.all_bps:
                structure: StructureWithInventory
                inventory = structure.inventory
                
                if inventory is None:
                    raise Exception(f"Structure {structure.object.uuid} has no inventory")

                bullet = Ammo.generate_from_template(Classes.equipment.ammo.advanced_rifle_bullet, save, inv_key)                
                structure.binary.replace_u32(structure.binary.set_property_position("NumBullets"), nr_of_stacks * 100)
                
                # while len(inventory.items) < nr_of_stacks:
                #     bullet.reidentify()
                #     save.add_obj_to_db(bullet.object.uuid, bullet.binary.byte_buffer)
                #     structure.add_item(bullet.object.uuid, save)

                # for key, item in inventory.items.items():
                #     item: Ammo
                #     if item.object.blueprint == Classes.equipment.ammo.advanced_rifle_bullet:
                #         item.set_quantity(100)
                #         save.modify_game_obj(key, item.binary.byte_buffer)

                for key, item in inventory.items.items():
                    item: Ammo
                    if item.object.blueprint == Classes.equipment.ammo.advanced_rifle_bullet:
                        item.set_quantity(100)
                        save.modify_game_obj(key, item.binary.byte_buffer)
                
                while len(inventory.items) < nr_of_stacks:
                    bullet.reidentify()
                    bullet.set_quantity(100)
                    save.add_obj_to_db(bullet.object.uuid, bullet.binary.byte_buffer)
                    structure.add_item(bullet.object.uuid)

                save.modify_game_obj(structure.object.uuid, structure.binary.byte_buffer)
                save.modify_game_obj(structure.inventory.object.uuid, structure.inventory.binary.byte_buffer)

    # def set_nr_of_element_in_generators(self, nr_of_element: int, save: AsaSave):
    #     nr_of_gens_handed = 0
    #     for _, structure in self.structures.items():
    #         if structure.object.blueprint in Classes.structures.placed.tek.generator:
    #             structure: StructureWithInventory
    #             if len(structure.inventory.items) == 0:
    #                 raise Exception(f"Structure {structure.object.uuid} has no inventory")
                
    #             element = Resource.generate_from_template(Classes.resources.Basic.element, save=save)
    #             element.set_quantity(nr_of_element)
    #             save.add_to_db(element)
    #             structure.inventory.add_item(element.object.uuid, save)
    #             nr_of_gens_handed += 1
                
    #             for key, _ in structure.inventory.items.copy().items():
    #                 if key != element.object.uuid:
    #                     structure.remove_item(key)

    #     return nr_of_gens_handed
    
    def set_nr_of_element_in_generators(self, nr_of_element: int, save: AsaSave):
        nr_of_gens_handed = 0                
        for _, structure in self.structures.items():
            if structure.object.blueprint in Classes.structures.placed.tek.generator:
                structure: StructureWithInventory
                if not structure.inventory:
                    raise Exception(f"Generators must have inventory!")

                # Reset the generators last checked fuel time to the current game time to prevent them from running out of fuel instantly
                structure.binary.replace_double(structure.binary.set_property_position("LastCheckedFuelTime"), save.save_context.game_time)
                
                element = Resource.generate_from_template(Classes.resources.Basic.element, save, structure.object.uuid)
                nr_of_gens_handed += 1

                for key, item in structure.inventory.items.items():
                    item: Resource
                    if structure.inventory.items[key].object.blueprint == Classes.resources.Basic.element:
                        item.set_quantity(1)
                        save.modify_game_obj(key, item.binary.byte_buffer)
                
                while len(structure.inventory.items) < nr_of_element:
                    element.reidentify()
                    element.set_quantity(1)
                    save.add_obj_to_db(element.object.uuid, element.binary.byte_buffer)
                    structure.add_item(element.object.uuid)

                save.modify_game_obj(structure.object.uuid, structure.binary.byte_buffer)
                save.modify_game_obj(structure.inventory.object.uuid, structure.inventory.binary.byte_buffer)

        return nr_of_gens_handed

    def import_from_binaries(self, path: Path):
        pass
