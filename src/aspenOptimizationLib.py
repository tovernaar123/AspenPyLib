import scipy as sc

def getTEAResult(aspenOutput):
    """ Placeholder function for TEA review functionality """
    blocksOutput = list(aspenOutput.keys())
    totalpower = 0
    print(aspenOutput)
    for blockName in blocksOutput:
        totalpower += float(aspenOutput[blockName]['Net Power'][0])

    return totalpower
    
# def aspenBlackBox(valuesArray, isBlock, paramArray, blockNameArray, getTeaResultFunc, blocksArray, dataVar, aspen, record_type, searchDict):
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
