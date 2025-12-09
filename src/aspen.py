from dataclasses import dataclass
from typing import Callable, Any

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


def get_all_children(node, parent=""):
    for i in range(node.Elements.Count):
        child = node.Elements.Item(i)

        yield child, rf"{parent}\{child.Name}"


@dataclass
class Res:
    name: str
    data: float
    unit: str


Fetcher = Callable[[Any, str], Res]


def fetch_from_data(path: str, output_name: str) -> Fetcher:
    def fetch(block, _block_path):
        b = block.FindNode(path)
        assert b is not None, f"couldn't find {path} for {block.Name}"
        return Res(output_name, b.Value, b.UnitString)

    return fetch


def fetch_from_connection(port: str, path: str, output_name: str) -> Fetcher:
    def fetch(block, block_path):
        p, *other = [b for b, _ in get_all_children(block.FindNode(rf"Ports\{port}"))]
        assert len(other) == 0, f"Multiple blocks connected to {port}. Expected 1 but got {1 + len(other)}"

        # need to read the stream relative to the block_path since we need to use the one from the closest hierarchy
        b = block.Application.Tree.FindNode(rf"{block_path}\..\..\Streams\{p.Value}\{path}")

        return Res(output_name, b.Value, b.UnitString)

    return fetch


DEFAULT_SEARCH: dict[str, list[Fetcher]] = {
    "Mixer": [fetch_from_connection("P(OUT)", r"Output\VOLFLMX2", "Outlet Flow")],
    "Flash2": [fetch_from_data(r"Output\B_PRES", "Outlet Pressure")],
    "Flash3": [fetch_from_data(r"Output\B_PRES", "Outlet Pressure")],
    "Decanter": [],  # TODO: Not in cstr-ch4.apw
    "Sep": [],  # TODO: figure out how to get pressure
    "Sep2": [],  # TODO: figure out how to get pressure
    # for the heater, not sure if the heating duty is `QNET` or `QCALC`
    "Heater": [fetch_from_data(r"Output\QCALC", "Heating Duty")],
    "HeatX": [
        fetch_from_data(r"Output\HX_AREAP", "Heat Transfer Area"),
        fetch_from_data(r"Output\HX_DUTY", "Duty"),
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
        fetch_from_data(r"Output\B_PRES", "Pressure"),
        fetch_from_data(r"Output\TOT_VOL", "Volume"),
    ],
    "RPlug": [],
    "RBatch": [],
    "RStoic": [
        fetch_from_data(r"Output\B_PRES", "Pressure")
    ],  # TODO: Find the length and width/ volume
    # TODO: Pump VFLOW is in cum/sec in Aspen, needs to be in L/sec
    "Pump": [fetch_from_data(r"Output\VFLOW", "Volumetric Flow")],
    "Compr": [fetch_from_data(r"Output\WNET", "Net Power")],
    "MCompr": [fetch_from_data(r"Output\WNET", "Net Power")],
    "Crytallizer": [],  # TODO: Not in cstr-ch4.apw
    "Crusher": [],  # TODO: Not in cstr-ch4.apw
    "Dryer": [],  # TODO: Not in cstr-ch4.apw
    "Fluidbed": [],  # TODO: Not in cstr-ch4.apw
    "Cyclone": [
        fetch_from_connection("G(OUT)", r"Output\VOLFLMX2", "Outlet Volumetric Gas Rate"),
    ],
    "Cfuge": [],  # TODO: Not in cstr-ch4.apw
    "Filter": [],  # TODO: Not in cstr-ch4.apw
    "CfFilter": [],  # TODO: Not in cstr-ch4.apw
    # Valve not in TEA?
}
HAP_RECORDTYPE = 6
# Port in or out
HAP_INOUT = 14


def read_data(aspen: Aspen, search: dict[str, list[Fetcher]] = DEFAULT_SEARCH):
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


def read_all_data(aspen: Aspen):
    data = {}

    blocks = list(
        get_all_children(
            aspen.Application.Tree.FindNode(r"\Data\Blocks"), r"\Data\Blocks"
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

def GetStreams(aspen: Aspen, search: dict[str, list[Fetcher]] = DEFAULT_SEARCH):
    data = {}

    blocks = list(
        get_all_children(
            aspen.Application.Tree.FindNode(r"\Data\Streams"), r"\Data\Streams"
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
