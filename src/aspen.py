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


def fetch_from_connection(port: str, path: str, output_name: str) -> Fetcher:
    def fetch(block: Block, block_path: str):
        p, *other = [b for b, _ in get_all_children(block.FindNode(rf"Ports\{port}"))]
        assert len(other) == 0, f"Multiple blocks connected to {port}. Expected 1 but got {1 + len(other)}"

        # need to read the stream relative to the block_path since we need to use the one from the closest hierarchy
        b = block.Application.Tree.FindNode(rf"{block_path}\..\..\Streams\{p.Value}\{path}")

        return Res(output_name, b.Value, b.UnitString)

    return fetch


DEFAULT_SEARCH: dict[str, list[Fetcher]] = {
    "Mixer": [fetch_from_connection("P(OUT)", r"Output\VOLFLMX2", "flow")],
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
        fetch_from_connection("G(OUT)", r"Output\VOLFLMX2", "Outlet Volumetric Gas Rate"),
    ],
    "Cfuge": [],  # TODO: Not in cstr-ch4.apw
    "Filter": [],  # TODO: Not in cstr-ch4.apw
    "CfFilter": [],  # TODO: Not in cstr-ch4.apw
    # Valve not in TEA?
}


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
