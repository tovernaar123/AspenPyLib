from dataclasses import dataclass, field
import win32com.client as win32

Aspen = win32.CDispatch


def init_aspen(filename: str):
    aspen = win32.gencache.EnsureDispatch("Apwn.Document")
    aspen.InitFromArchive2(filename)
    aspen.Visible = False
    aspen.SuppressDialogs = True

    return aspen


def run_aspen(aspen: Aspen):
    aspen.Engine.Run2()


def get_all_children(node, parent):
    for i in range(node.Elements.Count):
        child = node.Elements.Item(i)

        yield child, rf'{parent}\{child.Name}'


@dataclass
class SearchBlock:
    data: list[tuple[str, str]]
    children: list[str] = field(default_factory=list)

search = {
    "Hierarchy": SearchBlock([], [r"Data\Blocks"]),
    "Mixer": SearchBlock([]),
    "Flash2": SearchBlock([(r"Data\B_PRES", "Outlet Pressure")]),
    "Flash3": SearchBlock([(r"Data\B_PRES", "Outlet Pressure")]),
    "Decanter": SearchBlock([]),
    "Sep": SearchBlock([]),
    "Sep2": SearchBlock([]),
    # for the heater, not sure if the heating duty is `QNET` or `QCALC`
    "Heater": SearchBlock([(r"Data\QNET", "Heating Duty")]),
    # cannot find any data for heat exchangers
    "HeatX": SearchBlock([]),
    "MHeatX": SearchBlock([]),
    # All types of Columns


    # All types of Reactors
    "RStoic": SearchBlock([]),
    "RCSTR": SearchBlock([]),

    "Pump": SearchBlock([]),
    "Compr": SearchBlock([(r"Data\WNET", "Net Power")]),
    "MCompr": SearchBlock([(r"Data\WNET", "Net Power")]),
    "Crytallizer": SearchBlock([]),
    "Crusher": SearchBlock([]),
    "Dryer": SearchBlock([]),
    "Fluidbed": SearchBlock([]),
    "Cyclone": SearchBlock([]),
    "Cfuge": SearchBlock([]),
    "Filter": SearchBlock([]),
    "CfFilter": SearchBlock([]),
    "Valve": SearchBlock([]),
}
RECORD_TYPE = 6


def read_data(aspen: Aspen):
    data = {}

    blocks = list(get_all_children(aspen.Application.Tree.FindNode(r"\Data\Blocks"), r"\Data\Blocks"))

    # Loop through all blocks
    for block, path in blocks:
        record_type = block.AttributeValue(RECORD_TYPE)
        print(block.Name, block.Value, block.ValueType, record_type)

        curr_data = { "path": path, "record_type": record_type, "data": {} }

        if s := search.get(record_type):
            for b, data_path in get_all_children(block.FindNode("Output"), rf"{path}\Output"):
                curr_data["data"][b.Name] = (b.Value, b.UnitString)

            for child_path in s.children:
                b = block.FindNode(child_path)
                blocks.extend(get_all_children(b, path))

        data[block.Name] = curr_data

    return data
