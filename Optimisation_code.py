from dataclasses import dataclass
import win32com.client as win32
import sys
import scipy as sc
import time

from src.aspenOptimizationLib import listPossibleBlocksStreams, readAspen, optimizeInputs
from src.aspen import init_aspen, run_aspen

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

# CONNECT TO ASPEN FILE#
aspen = init_aspen(sys.argv[1])
run_aspen(aspen)

initialData = readAspen(aspen)
blocksList = list(initialData.keys())

listPossibleBlocksStreams(blocksList, aspen)

result = optimizeInputs([7], [5, 10], True, ["PRES"], ["COMP-1"], aspen)

print(result)
