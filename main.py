from dataclasses import dataclass
import win32com.client as win32
import sys

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

def changeInputVariable(blockName, parameterName, newParameterValue):
    node = aspen.Application.Tree.FindNode(rf"\Data\Blocks\{blockName}\Input\{parameterName}")
    print(node.Value)
    node.Value = float(newParameterValue)
    print(node.Value)
    
def getTEAResult(blocksArray, record_type, searchDict, dataVar):
    aspenOutput = readAspen(blocksArray, record_type, searchDict, dataVar)
    blocksOutput = list(aspenOutput.keys())
    totalpower = 0
    
    for blockName in blocksOutput:
        totalpower += float(aspenOutput[blockName]['Net Power'][0])

    return totalpower
    
def aspenBlackBox(valuesArray, paramArray, blockNameArray, getTeaResultFunc):
    if (len(paramArray) != len(blockNameArray) and len(paramArray) != len(valuesArray)):
        print("ERROR: enter correct number of parameters and blocks")
        sys.exit()
    
    for paramCount in range(len(paramArray)):
        paramPath = str(blockNameArray[paramCount]) + "\\Input\\" + str(paramArray[paramCount])
        paramNode = aspen.Application.Tree.FindNode(rf"\Data\Blocks\{paramPath}")
        paramNode.Value = float(valuesArray[paramCount])
        
    aspen.Save()
    aspen.Engine.Run2()
    cost = getTeaResultFunc()
    return cost
        
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
                blocks.extend(get_all_children(b))
    
    return dataVar
    
# Connect to Aspen Plus
print(f"Open file {sys.argv[1]}")
aspen = win32.gencache.EnsureDispatch("Apwn.Document")
aspen.InitFromArchive2(sys.argv[1])
aspen.Visible = False
aspen.SuppressDialogs = True  # Suppress windows dialogs

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

data = {}

def get_all_children(node):
    return (node.Elements.Item(i) for i in range(node.Elements.Count))

RECORD_TYPE = 6

blocks = list(get_all_children(aspen.Application.Tree.FindNode(r"\Data\Blocks")))

#output = readAspen(blocks, RECORD_TYPE, search, data)
#print(output)




