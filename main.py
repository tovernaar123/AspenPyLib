from dataclasses import dataclass
import win32com.client as win32
import sys

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

# Connect to Aspen Plus
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

# Loop through all blocks
for block in blocks:
    recordType = block.AttributeValue(RECORD_TYPE)
    print(block.Name, block.Value, block.ValueType, recordType)

    curr_data = {}

    if s := search.get(recordType):
        for path, name in s.data:
            b = block.FindNode(rf"Output\{path}")
            curr_data[name] = (b.Value, b.UnitString)
            data[block.Name] = curr_data

        for path in s.children:
            b = block.FindNode(rf"Data\{path}")
            blocks.extend(get_all_children(b))



print(data)