from .consumables import Consumables
from .placed_structures import PlacedStructures
from .dinos import Dinos
from .resources import Resources

class Structures:
    placed : PlacedStructures = PlacedStructures()

    all_bps = placed.all_bps

class Classes:
    consumables: Consumables = Consumables()
    structures: Structures = Structures()
    dinos: Dinos = Dinos()
    resources: Resources = Resources()

    all_bps = consumables.all_bps + structures.all_bps + dinos.all_bps + resources.all_bps