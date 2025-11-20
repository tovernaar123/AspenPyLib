from dataclasses import dataclass
import win32com.client as win32
import sys
import scipy as sc
import time

def get_all_children(node):
    return (node.Elements.Item(i) for i in range(node.Elements.Count))
    
def getTEAResult(aspen):
    """ Placeholder function for TEA review functionality """
    aspenOutput = readAspen(aspen)
    blocksOutput = list(aspenOutput.keys())
    totalpower = 0
    print(aspenOutput)
    for blockName in blocksOutput:
        totalpower += float(aspenOutput[blockName]['Net Power'][0])

    return totalpower
    
def aspenBlackBox(valuesArray, isBlock, paramArray, blockNameArray, aspen):        
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
    
def optimizeInputs(initialValues, bounds, isBlock, paramArray, blockNameArray, aspen):
    args = (isBlock, paramArray, blockNameArray, aspen)
    upperBound = bounds[1]
    lowerBound = bounds[0]
    limits = sc.optimize.Bounds(lowerBound, upperBound)
    result = sc.optimize.minimize(aspenBlackBox, initialValues, bounds=limits, method='trust-constr', args=args)
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
