class Stone:
    floor = "/Game/PrimalEarth/Structures/Stone/Stone_Floor/Floor_Stone.Floor_Stone_C"
    ceiling = "/Game/PrimalEarth/Structures/Stone/Stone_Ceiling/Ceiling_Stone.Ceiling_Stone_C"
    doorframe = "/Game/PrimalEarth/Structures/Tileset/DoorwayShort/Doorframe_Short_Stone.Doorframe_Short_Stone_C"
    wall = "/Game/PrimalEarth/Structures/Stone/Stone_Wall/Wall_Stone.Wall_Stone_C"
    beam = "/Game/PrimalEarth/Structures/Stone/Beam_Stone.Beam_Stone_C"
    triangle_foundation = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Stone/BP_TriFoundation_Stone.BP_TriFoundation_Stone_C"
    roof = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Roofs/Stone/StoneRoof_SM.StoneRoof_SM_C"
    door = "/Game/PrimalEarth/Structures/Tileset/DoorShort/Door_Short_Stone.Door_Short_Stone_C"
    gateframe = "/Game/PrimalEarth/Structures/Stone/Stone_GateFrame/GateFrame_Stone.GateFrame_Stone_C"
    pillar = "/Game/PrimalEarth/Structures/Stone/Stone_Pillar/Pillar_Stone.Pillar_Stone_C"
    tri_roof = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Stone/BP_TriRoof_Stone.BP_TriRoof_Stone_C"

    all_bps = [floor, ceiling, doorframe, wall, beam, triangle_foundation, roof, door, gateframe, pillar, tri_roof]
class Metal:
    floor = "/Game/PrimalEarth/Structures/Metal/Floor_Metal.Floor_Metal_C"
    wall = "/Game/PrimalEarth/Structures/Metal/Wall_Metal.Wall_Metal_C"
    triangle_foundation = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Metal/BP_TriFoundation_Metal.BP_TriFoundation_Metal_C"
    cliff_platform = "/Game/Aberration/Structures/CliffPlatforms/Metal_CliffPlatform/Metal_Platform_BP_Small.Metal_Platform_BP_Small_C"

    all_bps = [floor, wall, triangle_foundation, cliff_platform]

class Thatch:
    floor = "/Game/PrimalEarth/Structures/Thatch/Thatch_Floor.Thatch_Floor_C"

    all_bps = [floor]

class Tek:
    floor = "/Game/PrimalEarth/Structures/TekTier/Floor_Tek.Floor_Tek_C"
    generator = "/Game/PrimalEarth/Structures/StorageBox_TekGenerator.StorageBox_TekGenerator_C"

    all_bps = [floor, generator]
    
class Wood:
    spike_wall = "/Game/PrimalEarth/Structures/Wooden/SpikeWall.SpikeWall_C"
    crop_plot_large = "/Game/PrimalEarth/Structures/Wooden/CropPlotLarge_SM.CropPlotLarge_SM_C"
    floor = "/Game/PrimalEarth/Structures/Wooden/Floor_Wood_SM_New.Floor_Wood_SM_New_C"

    all_bps = [spike_wall, crop_plot_large, floor]

class Crafting:
    forge = "/Game/PrimalEarth/Structures/Forge.Forge_C"
    mortar_and_pestle = "/Game/PrimalEarth/Structures/MortarAndPestle.MortarAndPestle_C"
    compost_bin = "/Game/PrimalEarth/Structures/CompostBin.CompostBin_C"
    campfire = "/Game/PrimalEarth/Structures/Campfire.Campfire_C"
    cooking_pot = "/Game/PrimalEarth/Structures/CookingPot.CookingPot_C"

    all_bps = [forge, mortar_and_pestle, compost_bin, campfire, cooking_pot]

class Utility:
    simple_bed = "/Game/PrimalEarth/Structures/SimpleBed.SimpleBed_C"
    sleeping_bag = "/Game/PrimalEarth/Structures/SleepingBag.SleepingBag_C"
    anvil_bench = "/Game/PrimalEarth/Structures/StorageBox_AnvilBench.StorageBox_AnvilBench_C"
    small_storage_box = "/Game/PrimalEarth/Structures/StorageBox_Small.StorageBox_Small_C"
    large_bear_trap = "/Game/PrimalEarth/Structures/BearTrapLarge.BearTrapLarge_C"
    large_storage_box = "/Game/PrimalEarth/Structures/StorageBox_Large.StorageBox_Large_C"

    all_bps = [simple_bed, sleeping_bag, anvil_bench, small_storage_box, large_bear_trap, large_storage_box]
    
class TributeTerminals:
    tribute_terminal_purple = "/Game/PrimalEarth/Structures/TributeTerminal_Purple.TributeTerminal_Purple_C"
    tribute_terminal_red = "/Game/PrimalEarth/Structures/TributeTerminal_Red.TributeTerminal_Red_C"
    tribute_terminal_blue = "/Game/PrimalEarth/Structures/TributeTerminal_Blue.TributeTerminal_Blue_C"
    tribute_terminal_green = "/Game/PrimalEarth/Structures/TributeTerminal_Green.TributeTerminal_Green_C"

    all_bps = [tribute_terminal_purple, tribute_terminal_red, tribute_terminal_blue, tribute_terminal_green]

class Water:
    water_pipe_intake = "/Game/PrimalEarth/Structures/Pipes/WaterPipe_Stone_Intake.WaterPipe_Stone_Intake_C"
    water_tank = "/Game/PrimalEarth/Structures/BuildingBases/WaterTank_Metal.WaterTank_Metal_C"

    all_bps = [water_pipe_intake, water_tank]

class Turrets:
    auto = "/Game/PrimalEarth/Structures/BuildingBases/StructureTurretBaseBP.StructureTurretBaseBP_C"
    heavy = "/Game/PrimalEarth/Structures/BuildingBases/StructureTurretBaseBP_Heavy.StructureTurretBaseBP_Heavy_C"
    tek = "/Game/PrimalEarth/Structures/BuildingBases/StructureTurretTek.StructureTurretTek_C"

    all_bps = [auto, heavy, tek]

class Aberration:
    gas_collector = "/Game/Aberration/Structures/GasCollector/GasVein_Base_BP.GasVein_Base_BP_C"
    power_node = "/Game/Aberration/Structures/PowerNode/PrimalStructurePowerNode.PrimalStructurePowerNode_C"
    damaged_power_node = "/Game/Aberration/Structures/PowerNode/PrimalStructurePowerNode_Damaged.PrimalStructurePowerNode_Damaged_C"
    zipline_anchor = "/Game/Aberration/Structures/Zipline/Zipline_Anchor.Zipline_Anchor_C"
    gas_collector_asa = "/Game/Aberration/Structures/GasCollector/GasCollecter_ASA.GasCollecter_ASA_C"

    all_bps = [gas_collector, power_node, damaged_power_node, zipline_anchor, gas_collector_asa]


# class Frontier:
#     frontier_skin = "/Game/Packs/Frontier/Structures/Frontier/Skins/PrimalItemStructureSkin_Tileset_Frontier.PrimalItemStructureSkin_Tileset_Frontier_C"
#     train_car_platform = "/Game/Packs/Frontier/Structures/TrainCarts/PrimalItem_TrainCar_Platform.PrimalItem_TrainCar_Platform_C"

# class BobsTallTales:
#     steampunk_skin = "/Game/Packs/Steampunk/Structures/Tileset/PrimalItemStructureSkin_Tileset_Steampunk.PrimalItemStructureSkin_Tileset_Steampunk_C"

class PlacedStructures:
    stone: Stone = Stone()
    metal: Metal = Metal()
    thatch: Thatch = Thatch()
    tek: Tek = Tek()
    wood: Wood = Wood()
    crafting: Crafting = Crafting()
    utility: Utility = Utility()
    tribute_terminals: TributeTerminals = TributeTerminals()
    water: Water = Water()
    turrets: Turrets = Turrets()
    aberration: Aberration = Aberration()

    all_bps = stone.all_bps + metal.all_bps + thatch.all_bps + tek.all_bps + wood.all_bps + crafting.all_bps + utility.all_bps + tribute_terminals.all_bps + water.all_bps + turrets.all_bps + aberration.all_bps

