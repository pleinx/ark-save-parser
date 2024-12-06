from arkparse.classes.equipment import Saddles as SaddleBps

def __get_saddle_armor(bp: str):
    if bp in [SaddleBps.tapejara_tek, SaddleBps.rex_tek, SaddleBps.mosa_tek, SaddleBps.megalodon_tek, SaddleBps.rock_drake_tek]:
        return 45
    elif bp in [SaddleBps.paracer, SaddleBps.diplodocus, SaddleBps.bronto, SaddleBps.paracer_platform, SaddleBps.archelon, SaddleBps.carbo]:
        return 20
    elif bp == SaddleBps.titanosaur_platform:
        return 1
    else:
        return 25
    
def __get_saddle_dura(bp: str):
    if bp in [SaddleBps.tapejara_tek, SaddleBps.rex_tek, SaddleBps.mosa_tek, SaddleBps.megalodon_tek, SaddleBps.rock_drake_tek]:
        return 120
    elif bp == SaddleBps.mole_rat:
        return 500
    else:
        return 100
