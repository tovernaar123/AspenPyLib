from dataclasses import dataclass
import win32com.client as win32
import sys
import scipy as sc
import time

sys.path.append("src")
import src.aspenOptimizationLib as aol

@dataclass
class SearchBlock:
    data: list[tuple[str, str]]
    children: list[str]

search = {
    "Hierarchy": SearchBlock([], ["Blocks"]),
    "Compr": SearchBlock([("WNET", "Net Power")], []),
    "MCompr": SearchBlock([("WNET", "Net Power")], []),
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

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

    
#CONNECT TO ASPEN FILE#
#print(f"Open file {sys.argv[1]}")
aspen = win32.gencache.EnsureDispatch("Apwn.Document")
aspen.InitFromArchive2(sys.argv[1])
aspen.Visible = False
aspen.SuppressDialogs = True  # Suppress windows dialogs
aspen.Engine.Run2()

data = {}

RECORD_TYPE = 6

blocks = list(aol.get_all_children(aspen.Application.Tree.FindNode(r"\Data\Blocks")))

initialData = aol.readAspen(blocks, RECORD_TYPE, search, data)
blocksList = list(initialData.keys())
trueFeedStreams = []
trueOutputStreams = []
    
aol.listPossibleBlocksStreams(blocksList, aspen, trueFeedStreams, trueOutputStreams)

result = aol.optimizeInputs([7],
            [5, 10],
            aol.aspenBlackBox,
            True,
            ["PRES"],
            ["COMP-1"],
            aol.getTEAResult,
            blocks,
            data, 
            aspen,
            RECORD_TYPE,
            search)
            
print(result)







