import sys
from dataclasses import dataclass
import win32com.client as win32
import src.inout as inout
import src.aspenOptimizationLib as aol
from src.aspen import init_aspen, read_data, run_aspen
from os.path import abspath


if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

# Connect to Aspen Plus
aspen = init_aspen(abspath(sys.argv[1]))

run_aspen(aspen)

plant_configuration = read_data(aspen)

#inout.write_JSON(data, "./data.json")
#plant_configuration = inout.read_JSON("./data.json")

print(plant_configuration)
Plant_object = inout.TEA_config(plant_configuration)

IDV_list = plant_configuration.keys()

aol.listPossibleBlocksStreams(IDV_list, aspen)
# initialValues, bounds, isBlock, paramArray, blockNameArray, aspen
result = aol.optimizeInputs([7],
                            (5, 10),
                            True,
                            ["PRES"],
                            ["COMP-1"],
                            aspen)

print(result)
