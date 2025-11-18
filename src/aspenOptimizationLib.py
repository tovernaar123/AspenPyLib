from dataclasses import dataclass
import win32com.client as win32
import sys
import scipy as sc
import time

def get_all_children(node):
    return (node.Elements.Item(i) for i in range(node.Elements.Count))
    
def getTEAResult(blocksArray, record_type, searchDict, dataVar):
    """ Placeholder function for TEA review functionality """
    aspenOutput = readAspen(blocksArray, record_type, searchDict, dataVar)
    blocksOutput = list(aspenOutput.keys())
    totalpower = 0
    #print(aspenOutput)
    
    for blockName in blocksOutput:
        totalpower += float(aspenOutput[blockName]['Net Power'][0])

    return totalpower
    
def aspenBlackBox(valuesArray, isBlock, paramArray, blockNameArray, getTeaResultFunc, blocksArray, dataVar, aspen, record_type, searchDict):
    if (len(paramArray) != len(blockNameArray) and len(paramArray) != len(valuesArray)):
        print("ERROR: enter correct number of parameters and blocks")
        sys.exit()
        
    if isBlock == True:
        typename = "Blocks"
    else:
        typename = "Streams"
    
    for paramCount in range(len(paramArray)):
        paramPath = str(blockNameArray[paramCount]) + "\\Input\\" + str(paramArray[paramCount])
        #print(rf"\Data\{typename}\{paramPath}")
        paramNode = aspen.Application.Tree.FindNode(rf"\Data\{typename}\{paramPath}")
        
        if paramNode is None:
            print("BAD PATH:", rf"\Data\{typename}\{paramPath}")
            raise Exception("Node not found")
        #print(valuesArray[paramCount])
        paramNode.Value = float(valuesArray[paramCount])
        
    aspen.Engine.Run2()
    cost = getTeaResultFunc(blocksArray, record_type, searchDict, dataVar)
    return cost
    
def optimizeInputs(initialValues, bounds, blackBoxFunc, isBlock, paramArray, blockNameArray, getTeaResultsFunc, blocksArray, dataVar, aspenItem, record_type, searchDict):
    argumentsArr = (isBlock, paramArray, blockNameArray, getTeaResultsFunc, blocksArray, dataVar, aspenItem, record_type, searchDict)
    upperBound = bounds[1]
    lowerBound = bounds[0]
    limits = sc.optimize.Bounds(lowerBound, upperBound)
    result = sc.optimize.minimize(blackBoxFunc, initialValues, bounds=limits, method='trust-constr', args=argumentsArr)
    return result
    
        
def readAspen(blocksVar, RECORD_TYPE, searchDict, dataVar):
    # Loop through all blocks
    for block in blocksVar:
        recordType = block.AttributeValue(RECORD_TYPE)
        #print(block.Name, block.Value, block.ValueType, recordType)

        curr_data = {}

        if s := searchDict.get(recordType):
            for path, name in s.data:
                b = block.FindNode(rf"Output\{path}")
                curr_data[name] = (b.Value, b.UnitString)
                dataVar[block.Name] = curr_data

            for path in s.children:
                b = block.FindNode(rf"Data\{path}")
                blocksVar.extend(get_all_children(b))
    
    return dataVar
    
def listPossibleBlocksStreams(blockNameList, aspenItem, trueFeed, trueOutput):
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
