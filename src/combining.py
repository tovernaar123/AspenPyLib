import sys
from dataclasses import dataclass
import win32com.client as win32
import inout
import aspenOptimizationLib as aol

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

# Connect to Aspen Plus
aspen = win32.gencache.EnsureDispatch("Apwn.Document") # type: ignore
aspen.InitFromArchive2(sys.argv[1])
aspen.Visible = False
aspen.SuppressDialogs = True  # Suppress windows dialogs
aspen.Engine.Run2()



#inout.write_JSON(data, "./data.json")
#plant_configuration = inout.read_JSON("./data.json")

# print(plant_configuration)
# initialValues, bounds, isBlock, paramArray, blockNameArray, aspen
result = aol.optimizeInputs([7],
                            (5, 10),
                            True,
                            ["PRES"],
                            ["COMP-1"],
                            aspen)

print(result)
