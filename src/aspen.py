from dataclasses import dataclass
from typing import Callable, Any, TypeAlias

import win32com.client as win32

Aspen: TypeAlias = win32.CDispatch


def init_aspen(filename: str):
    aspen = win32.gencache.EnsureDispatch("Apwn.Document")
    aspen.InitFromArchive2(filename)
    aspen.Visible = False
    aspen.SuppressDialogs = True

    return aspen


def run_aspen(aspen: Aspen):
    aspen.Engine.Run2()


def get_all_children(node, parent=""):
    for i in range(node.Elements.Count):
        child = node.Elements.Item(i)

        yield child, rf"{parent}\{child.Name}"


@dataclass
class Res:
    name: str
    data: float
    unit: str

HAP_RECORDTYPE = 6
# Port in or out
HAP_INOUT = 14
HAP_UNITROW = 2
HAP_UNITCOL = 3
HAP_HASCHILDREN = 38
HAP_VALUE = 0

Block: TypeAlias = Any

Fetcher = Callable[[Block, str], Res]

def get_value_with_unit(block: Block, unit: str):
    unit_row = block.AttributeValue(HAP_UNITROW)
    unit_table = block.Application.Tree.FindNode(r"\Unit Table")

    # subtracting by 1 since the table starts at 1 but .Item(...) starts at 0
    row = unit_table.Elements.Item(unit_row - 1)

    # this is quoted so that if the unit contains a / it still works
    # for example `l/sec`
    unit_block = row.FindNode(f"'{unit}'")

    assert unit_block is not None, f"Couldn't find '{unit}' in {row.Name}"

    return block.ValueForUnit(unit_row, unit_block.Value)


def fetch_from_data(path: str, output_name: str, unit: str) -> Fetcher:
    def fetch(block: Block, _block_path: str):
        b = block.FindNode(path)
        assert b is not None, f"couldn't find {path} for {block.Name}"
        return Res(output_name, get_value_with_unit(b, unit), unit)

    return fetch


def fetch_from_connection(port: str, path: str, output_name: str, unit: str) -> Fetcher:
    def fetch(block: Block, block_path: str):
        p, *other = [b for b, _ in get_all_children(block.FindNode(rf"Ports\{port}"))]
        assert len(other) == 0, f"Multiple blocks connected to {port}. Expected 1 but got {1 + len(other)}"

        # need to read the stream relative to the block_path since we need to use the one from the closest hierarchy
        b = block.Application.Tree.FindNode(rf"{block_path}\..\..\Streams\{p.Value}\{path}")

        return Res(output_name, get_value_with_unit(b, unit), unit)

    return fetch


DEFAULT_SEARCH: dict[str, list[Fetcher]] = {
    "Mixer": [fetch_from_connection("P(OUT)", r"Output\VOLFLMX2", "flow", "l/sec")],
    "Flash2": [fetch_from_data(r"Output\B_PRES", "Outlet Pressure", "bar")],
    "Flash3": [fetch_from_data(r"Output\B_PRES", "Outlet Pressure", "bar")],
    "Decanter": [],  # TODO: Not in cstr-ch4.apw
    "Sep": [],  # TODO: figure out how to get pressure
    "Sep2": [],  # TODO: figure out how to get pressure
    # for the heater, not sure if the heating duty is `QNET` or `QCALC`
    "Heater": [fetch_from_data(r"Output\QCALC", "Heating Duty", "MW")],
    "HeatX": [
        fetch_from_data(r"Output\HX_AREAP", "Heat Transfer Area", "sqm"),
        fetch_from_data(r"Output\HX_DUTY", "Duty", "MW"),
    ],
    # "MHeatX": SearchBlock([]),
    # All types of Columns
    "DSTWU": [],
    "Distl": [],
    "SCFrac": [],
    "RadFrac": [],
    "MultiFrac": [],
    "PetroFrac": [],
    "RateFrac": [],
    # All types of Reactor
    "RYield": [],
    "REquil": [],
    "RGibbs": [],
    "RCSTR": [
        fetch_from_data(r"Output\B_PRES", "Pressure", "bar"),
        fetch_from_data(r"Output\TOT_VOL", "Volume", "cum"),
    ],
    "RPlug": [],
    "RBatch": [],
    "RStoic": [
        fetch_from_data(r"Output\B_PRES", "Pressure", "bar")
    ],  # TODO: Find the length and width/ volume
    "Pump": [fetch_from_data(r"Output\VFLOW", "Volumetric Flow", "l/sec")],
    "Compr": [fetch_from_data(r"Output\WNET", "Net Power", "kW")],
    "MCompr": [fetch_from_data(r"Output\WNET", "Net Power", "kW")],
    "Crytallizer": [],  # TODO: Not in cstr-ch4.apw
    "Crusher": [],  # TODO: Not in cstr-ch4.apw
    "Dryer": [],  # TODO: Not in cstr-ch4.apw
    "Fluidbed": [],  # TODO: Not in cstr-ch4.apw
    "Cyclone": [
        fetch_from_connection("G(OUT)", r"Output\VOLFLMX2", "Outlet Volumetric Gas Rate", "cum/sec"),
    ],
    "Cfuge": [],  # TODO: Not in cstr-ch4.apw
    "Filter": [],  # TODO: Not in cstr-ch4.apw
    "CfFilter": [],  # TODO: Not in cstr-ch4.apw
    # Valve not in TEA?
}


def read_data(aspen: Aspen, search=None):
    if search is None:
        search = DEFAULT_SEARCH

    data = {}

    blocks = list(
        get_all_children(
            aspen.Application.Tree.FindNode(r"\Data\Blocks"), r"\Data\Blocks"
        )
    )

    for block, path in blocks:
        record_type = block.AttributeValue(HAP_RECORDTYPE)

        print(block.Name, record_type, path)

        curr_data = {
            "path": path,
            "record_type": record_type,
            "data": {},
        }

        if fetchers := search.get(record_type):
            for fetch in fetchers:
                res = fetch(block, path)
                curr_data["data"][res.name] = (res.data, res.unit)

            if len(fetchers) != 0:
                data[path] = curr_data
        elif record_type == "Hierarchy":
            child_path = r"Data\Blocks"
            b = block.FindNode(child_path)
            blocks.extend(get_all_children(b, rf"{path}\{child_path}"))

    return data


def read_all_units(aspen: Aspen):
    units = {
        u.Name: {
            "value": u.Value,
            "children": {c.Name: c.Value for c, _ in get_all_children(u)},
        }
        for u, _ in get_all_children(aspen.Application.Tree.FindNode(r"\Unit Table"))}

    return units


def read_all_data(aspen: Aspen):
    data = {}

    blocks = list(
        get_all_children(
            aspen.Application.Tree.FindNode(r"\Data\Blocks"), r"\Data\Blocks"
        ))

    blocks.extend(
        get_all_children(
            aspen.Application.Tree.FindNode(r"\Data\Streams"), r"\Data\Streams"
        )
    )

    # Loop through all blocks
    for block, path in blocks:
        record_type = block.AttributeValue(HAP_RECORDTYPE)
        print(block.Name, block.Value, block.ValueType, record_type)

        curr_data = {
            "path": path,
            "record_type": record_type,
            "data": {},
            "input": {},
            "connections": {},
        }

        for b, _ in get_all_children(block.FindNode("Input")):
            curr_data["input"][b.Name] = (b.Value, b.UnitString)

        for b, _ in get_all_children(block.FindNode("Output")):
            curr_data["data"][b.Name] = (b.Value, b.UnitString)

        for b, _ in get_all_children(block.FindNode("Connections")):
            curr_data["connections"][b.Name] = (
                b.Value,
                b.AttributeValue(HAP_INOUT),
            )

        if record_type == "Hierarchy":
            child_path = r"Data\Blocks"
            b = block.FindNode(child_path)
            blocks.extend(get_all_children(b, rf"{path}\{child_path}"))

        data[block.Name] = curr_data

    return data

def MassSearch(MASSFLOW,vocal = True)->dict:
    """
    this function returns a dictionary with all Massflows in the current directory in kg/h
    
    :param MASSFLOW: an Aspen object
    :param vocal: BOOL print useless stuff
    :return: rerturns an dictionary with all massflows
    :rtype: dict
    """
    data = {r"\CIPSD":{},
            r"\MIXED":{}}
    
    # masses = list(
    #     get_all_children(
    #         stream.FindNode(rf"Output\MASSFLOW\CIPSD"), rf"Output\MASSFLOW\CIPSD"
    #     )
    # )
    MIXED = list(get_all_children(MASSFLOW.FindNode(r"MIXED")))
    CIPSD = list(get_all_children(MASSFLOW.FindNode(r"CIPSD")))
    for mass,path in CIPSD:
        if mass.Value != None:
            data[r"\CIPSD"][rf"{path[1:]}"] = mass.Value
        else:
            data[r"\CIPSD"][rf"{path[1:]}"] = 0
    
    
    for mass,path in MIXED:
        if mass.Value != None:
            data[r"\MIXED"][rf"{path[1:]}"] = mass.Value
        else:
            data[r"\MIXED"][rf"{path[1:]}"] = 0
            
            
    return data
    # mass = mass.Findnode(rf"Output/MASSFLOW/CIPSD")


def StreamSearch(stream,path,vocal = True):
    data = {}

    # stream = aspen.Application.Tree.FindNode(rf"{path}")

    # print(stream)
    # print(rf"stream.FindNode({path}\Ports\SOURCE)")
    
    port = stream.FindNode(rf"Ports\SOURCE")
    # print(port)
    if vocal:
        print(f"    has parent: {port.AttributeValue(HAP_HASCHILDREN)}")
    
    if port.AttributeValue(HAP_HASCHILDREN) == False:
        if vocal:
            print(rf"   {path} is parentless")
        data[rf"{path}"] = {}
        data[rf"{path}"][r"SOURCE"] = {"cost/h":0}
        data[rf"{path}"][r"MASSFLOW"] = MassSearch(MASSFLOW=stream.FindNode(r"\Output\MASSFLOW"))
        
        if stream.FindNode(r"Output\STCOST").AttributeValue(0) != None:
            data[rf"{path}"][r"SOURCE"]["cost/h"] = float(stream.FindNode(r"Output\STCOST").AttributeValue(0))
            
        # else:
        #     data[rf"{path}"][r"SOURCE"]["cost/h"] = 0
        if vocal:
            print(f"    cost/h: {data[rf"{path}"][r"SOURCE"]["cost/h"]}")
                
    return data
            
    
def GetStreams(aspen: Aspen,vocal = True):
    """
    This functions creates an dictionary with as indices the path to the objects
    MASSFLOW is in kg/h
    
    :param aspen: the Asping object with which the file is treveresd
    :param vocal: True makes the function print more information
    """
    #todo catfeed is fucked up

    data = {}
    streams = list(
        get_all_children(
            aspen.Application.Tree.FindNode(r"\Data\Streams"), r"\Data\Streams"
        )
    )
    blocks = list(
        get_all_children(
            aspen.Application.Tree.FindNode(r"\Data\Blocks"), r"\Data\Blocks"
        )
    )

    for block, path in blocks:
        # print(block)
        
        record_type = block.AttributeValue(HAP_RECORDTYPE)

        if record_type == "Hierarchy":
            child_path = r"Data\Blocks"
            b = block.FindNode(child_path)
            s = block.FindNode(r"Data\Streams")
            blocks.extend(get_all_children(b, rf"{path}\{child_path}"))
            streams.extend(get_all_children(s,rf"{path}\Data\Streams"))
    if vocal:
        print(f"streams found: {streams}")
    for (stream, path) in streams:
        if vocal:
            # print(stream)
            print("\n-----",path,"----- type:",type(stream))
        data.update(StreamSearch(stream=stream,path=path,vocal = vocal))

    
    if vocal:
        pprint(data)
        
    return data

if __name__ == "__main__":
    from os.path import abspath
    import sys
    from pprint import pprint
    aspen = init_aspen(abspath(sys.argv[1]))
    print(aspen)
    pprint(GetStreams(aspen=aspen,vocal=False))