from pathlib import Path
from importlib.resources import files

package = 'arkparse.assets'
with open(files(package) / f'tamable_dinos.txt', 'r', encoding='utf-8') as f:
    TAMABLE_CLASSNAMES = set(line.strip() for line in f if line.strip())

def is_tamable(dino) -> bool:
    dino_class = dino.get_short_name() + "_C"
    return dino_class in TAMABLE_CLASSNAMES
