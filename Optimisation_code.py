from dataclasses import dataclass
import win32com.client as win32
import sys
import scipy as sc
import time

sys.path.append("src")
import src.aspenOptimizationLib as aol



if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

    
#CONNECT TO ASPEN FILE#
aspen = win32.gencache.EnsureDispatch("Apwn.Document")
aspen.InitFromArchive2(sys.argv[1])
aspen.Visible = False
aspen.SuppressDialogs = True  # Suppress windows dialogs
aspen.Engine.Run2()

initialData = aol.readAspen(aspen)
blocksList = list(initialData.keys())

aol.listPossibleBlocksStreams(blocksList, aspen)
# initialValues, bounds, isBlock, paramArray, blockNameArray, aspen
result = aol.optimizeInputs([7],
            [5, 10],
            True,
            ["PRES"],
            ["COMP-1"],
            aspen)
            
print(result)