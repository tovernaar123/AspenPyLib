from dataclasses import dataclass
import win32com.client as win32
import sys
import scipy as sc
import time
from . import TeaIntegration as inout
from typing import Sequence,Tuple, TypeAlias,Union
from numpy.typing import NDArray
import numpy as np
from openpytea.plant import Plant
from scipy.optimize import Bounds, minimize

def get_all_children(node):
    return (node.Elements.Item(i) for i in range(node.Elements.Count))

def CreatePlant(aspen) -> Plant:
    plant_configuration = inout.readAspen(aspen)
    Plant_object = inout.TEA_plant(plant_configuration, plant_configuration)
    return Plant_object

def getTEAResult(aspen) -> float:
    """ Placeholder function for TEA review functionality """
    Plant_object = CreatePlant(aspen)
    Plant_object.calculate_variable_opex() 
    variable:float =  Plant_object.variable_production_costs
    Plant_object.calculate_fixed_opex()
    fixed: float = Plant_object.fixed_production_costs
    return variable + fixed
    
# def aspenBlackBox(valuesArray, isBlock, paramArray, blockNameArray, getTeaResultFunc, blocksArray, dataVar, aspen, record_type, searchDict):
def aspenBlackBox(
    valuesArray:NDArray[np.float64], 
    isBlock:bool, 
    paramArray:Sequence[str], 
    blockNameArray:Sequence[str], 
    aspen
    ) -> float:        
    assert not (len(paramArray) != len(blockNameArray) and len(paramArray) != len(valuesArray)), (
        "ERROR: enter correct number of parameters and blocks"
    )
    if isBlock == True:
        typename = "Blocks"
    else:
        typename = "Streams"
    
    for param, blockName, value in zip(paramArray, blockNameArray, valuesArray):
        paramPath = str(blockName) + "\\Input\\" + str(param)
        #print(rf"\Data\{typename}\{paramPath}")
        paramNode = aspen.Application.Tree.FindNode(rf"\Data\{typename}\{paramPath}")
        
        if paramNode is None:
            print("BAD PATH:", rf"\Data\{typename}\{paramPath}")
            raise Exception("Node not found")
        #print(valuesArray[paramCount])
        paramNode.Value = float(value)
        
    aspen.Engine.Run2()
    cost = getTEAResult(aspen)
    return cost

BoundsType:TypeAlias = Union[
    Tuple[float, float],
    Tuple[Sequence[float], Sequence[float]], 
]

def optimizeInputs(
    initialValues:Sequence[float], 
    bounds:BoundsType, 
    isBlock:bool, 
    paramArray:Sequence[str], 
    blockNameArray:Sequence[str], 
    aspen
    ):
    args = (isBlock, paramArray, blockNameArray, aspen)
    upperBound = bounds[1]
    lowerBound = bounds[0]
    limits = Bounds(lb = lowerBound, ub= upperBound)
    
    
    result = minimize(aspenBlackBox, initialValues, bounds=limits, method='trust-constr', args=args)
    return result

@dataclass
class SearchBlock:
    data: list[tuple[str, str]]
    children: list[str]

SearchDefault = {
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
RECORD_TYPE = 6

def readAspen(aspen, search=SearchDefault):
    data = {}
    blocks = list(get_all_children(aspen.Application.Tree.FindNode(r"\Data\Blocks")))
    # Loop through all blocks
    for block in blocks:
        recordType = block.AttributeValue(RECORD_TYPE)
        # print(block.Name, block.Value, block.ValueType, recordType)
        curr_data = {}
        if s := search.get(recordType):
            for path, name in s.data:
                b = block.FindNode(rf"Output\{path}")
                curr_data[name] = (b.Value, b.UnitString)
                data[block.Name] = curr_data
            for path in s.children:
                b = block.FindNode(rf"Data\{path}")
                blocks.extend(get_all_children(b))
    return data
    
def listPossibleBlocksStreams(blockNameList, aspenItem):
    inputStreams = []
    outputStreams = []
    
    for block in blockNameList:
        connections = aspenItem.Application.Tree.FindNode(rf"\Data\Blocks\{block}\Connections")
        
        if (connections is not None):
            elements = connections.Elements.Count
            for i in range(0, elements):
                stream = connections.Elements.Item(i)

                inputOrOutputNode = aspenItem.Application.Tree.FindNode(rf"\Data\Blocks\{block}\Connections\{stream.Name}")
                inOrOut = str(inputOrOutputNode.Value)
                if inOrOut == "F(IN)":
                    inputStreams.append(stream.Name)
                else:
                    outputStreams.append(stream.Name)
                
    trueFeed = set(inputStreams) - set(outputStreams)
    trueOutput = set(outputStreams) - set(inputStreams)

    print(f"Possible Blocks: {blockNameList}")
    print(f"Possible True Feed Streams: {trueFeed}")
    print(f"Possible True Output Streams: {trueOutput}")
