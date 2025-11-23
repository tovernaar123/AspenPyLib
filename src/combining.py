import sys
from dataclasses import dataclass
import win32com.client as win32
import inout
import aspenOptimizationLib as aol

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

# Connect to Aspen Plus
aspen = win32.gencache.EnsureDispatch("Apwn.Document")
aspen.InitFromArchive2(sys.argv[1])
aspen.Visible = False
aspen.SuppressDialogs = True  # Suppress windows dialogs
aspen.Engine.Run2()

@dataclass
class SearchBlock:
    data: list[tuple[str, str]]
    children: list[str]

search = {
    "Hierarchy": SearchBlock([], ["Blocks"]),
    "Compr": SearchBlock([("WNET", "Net Power")], []),
    "MCompr": SearchBlock([("WNET", "Net Power")], []),
    "Turb": SearchBlock([("WNET", "Net Power")], []),
    "Cyclone": SearchBlock([], []),
    "Sep": SearchBlock([], []),
    "HeatX": SearchBlock([], []),
    "Dupl": SearchBlock([], []),
    "Flash2": SearchBlock([], []),
    "Heater": SearchBlock([], []),
    "Mixer": SearchBlock([], []),
    "Sep2": SearchBlock([], []),
    "RPlug": SearchBlock([], []),
    "Valve": SearchBlock([], []),
    "RStoic": SearchBlock([], []),
}

plant_configuration = inout.readAspen(aspen, search, 6)

#inout.write_JSON(data, "./data.json")
#plant_configuration = inout.read_JSON("./data.json")

print(plant_configuration)
Plant_object = inout.TEA_plant(plant_configuration, plant_configuration)

IDV_list = plant_configuration.keys()

aol.listPossibleBlocksStreams(IDV_list, aspen)
# initialValues, bounds, isBlock, paramArray, blockNameArray, aspen
result = aol.optimizeInputs([7],
                            [5, 10],
                            True,
                            ["PRES"],
                            ["COMP-1"],
                            aspen)

print(result)
