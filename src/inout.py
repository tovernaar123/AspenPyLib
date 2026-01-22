"""
functions for making and loading JSONs, and also turning data into TEA things

by: Johannes

p.s: json things are basically just wrappers right now.
"""
import sys
import json
from typing import TypeAlias, Union, Literal
import numpy as np
from dataclasses import dataclass
# someone better versed in python make this pretty
from openpytea.plant import Plant
from openpytea.equipment import *
from openpytea.analysis import *
"""
TODO:
- [] add process plant creation
- [] make actual docstrings 


"""
def get_all_children(node):
    return (node.Elements.Item(i) for i in range(node.Elements.Count))

def write_JSON(data, path)->None:
    """
    saves to the given file path, also formats the data (if necessary)
    """
    # make this a method if we make the data into objects

    # format data here (nothing currently)

    with open(path, "w") as file:
        json.dump(data, file)
    file.close()

def read_JSON(path)->dict:
    """
    inverse of the other thing, also un-formats the data (if neccessary)
    """

    with open(path, "r") as file:
        data = json.load(file)
    file.close()
    
    # unformat data here (nothing currently)

    return data

VariableOpexInputs:TypeAlias = dict[str,dict[Union[Literal["consumption"],Literal["price"]], float]]

def get_variable_opex_inputs(stream_data:dict, block_data_dict:dict, prices:dict, electricity_price: float)->VariableOpexInputs:
    variable_opex_inputs = {}

    net_power_consumption = 0 #in kW!
    for block in block_data_dict.values():
        try:
            net_power_consumption += block["data"]["Net Power"][0]
        except KeyError:
            pass
    variable_opex_inputs["electricity"] = {
        "consumption" : net_power_consumption * 24,
        "price" : electricity_price
    }
    
    for stream in (s for s in stream_data.values() if not s["has_source"]):
        stream_name = stream["path"]
        cost = stream["cost/h"] or 0
        if cost != 0:
            consumption = 0
            for flowrates in list(stream["MASSFLOW"]["MIXED"].keys()):
                consumption += stream["MASSFLOW"]["MIXED"][rf"{flowrates}"]
            variable_opex_inputs[stream_name] = {}
            variable_opex_inputs[stream_name]["consumption"] = consumption * 24 #DAILY
            variable_opex_inputs[stream_name]["price"] = cost / consumption #was hourly, now PER UNIT
        else:
            for substance_name in stream["MASSFLOW"]["MIXED"].keys():
                if substance_name not in variable_opex_inputs:
                    variable_opex_inputs[substance_name] = {
                        "consumption": 0,
                        "price": 0
                    }

                variable_opex_inputs[substance_name]["consumption"] += \
                    (stream["MASSFLOW"]["MIXED"][rf"{substance_name}"] * 24) #DAILY
                if rf"{substance_name}" in prices:
                    variable_opex_inputs[rf"{substance_name}"]["price"] =  prices[rf"{substance_name}"]
                else:
                    sys.exit(rf"No given price for {substance_name}")
        
    return variable_opex_inputs

PlantProducts: TypeAlias = dict[str,dict[Union[Literal["production"],Literal["price"]], float]]

def get_plant_products(stream_data:dict, prices:dict) -> PlantProducts:
    plant_products = {}

    for stream in (s for s in stream_data.values() if not s["has_dest"]):
        stream_name = stream["path"]
        cost = stream["cost/h"] or 0
        if cost != 0:
            production = 0
            for flowrates in list(stream["MASSFLOW"]["MIXED"].keys()):
                production += stream["MASSFLOW"]["MIXED"][rf"{flowrates}"]

            plant_products[stream_name] = {}
            plant_products[stream_name]["production"] = production * 24 #DAILY
            plant_products[stream_name]["price"] = cost / production #was hourly, now PER UNIT
        else:
            for substance_name in stream["MASSFLOW"]["MIXED"].keys():
                if substance_name not in plant_products:
                    plant_products[substance_name] = {
                        "production": 0,
                        "price": 0
                    }

                plant_products[substance_name]["production"] += \
                    (stream["MASSFLOW"]["MIXED"][rf"{substance_name}"] * 24) #DAILY
                if rf"{substance_name}" in prices:
                    plant_products[rf"{substance_name}"]["price"] =  prices[rf"{substance_name}"]
                else:
                    sys.exit(rf"No given price for {substance_name}")

    return plant_products


@dataclass
class BlockEntry:
    type: str
    category: str
    paramater_name:str


EquipmentConfig: dict[str, BlockEntry] = {
    "Mixer":       BlockEntry("Static mixer", "Agitators, blenders, & mixers", "flow"),

    # TODO: Should be shell mass instead of Outlet Pressure
    "Flash2":      BlockEntry("Vertical CS", "Pressure vessels", "Outlet Pressure"),
    "Flash3":      BlockEntry("Vertical CS", "Pressure vessels", "Outlet Pressure"),

    "Decanter":    BlockEntry("Horizontal CS", "Pressure vessels", "flow"), 
    "Sep":         BlockEntry("Vertical CS", "Pressure vessels", "flow"), 
    "Sep2":        BlockEntry("Vertical CS", "Pressure vessels", "flow"),

    # TODO: need to handle negative duty somehow
    "Heater":      BlockEntry("Furnace, cylindrical", "Boilers, heaters, & furnaces", "Heating Duty"),

    "HeatX":       BlockEntry("U-tube shell & tube", "Heat exchangers", "Heat Transfer Area"), 
    "MHeatX":      BlockEntry("U-tube shell & tube", "Heat exchangers", "Heat Transfer Area"),

    "RYield":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),
    "REquil":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),
    "RGibbs":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),
    "RCSTR":       BlockEntry("Jacketed agitated",  "Reactors", "Volume"),
    # TODO: Add RStoic
    "RYield":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),


    "Pump":        BlockEntry("Single-stage centrifugal","Pumps","Volumetric Flow"),

    # TODO: Handle negative power
    "Compr":       BlockEntry("Compressor, centrifugal","Compressors, fans, & blowers","Net Power"),
    "MCompr":       BlockEntry("Compressor, centrifugal","Compressors, fans, & blowers","Net Power"),

    "Crytallizer": BlockEntry("Scraped surface crystallizer","Crystallizers",""),
    "Crusher":     BlockEntry("Pulverizer","Crushers",""),
    "Dryer":       BlockEntry("Direct contact rotary dryer","Dryers",""),
    "Fluidbed":    BlockEntry("Indirect fluidized-bed","Reactors",""),
    "Cyclone":     BlockEntry("Gas multi-cyclone","Dust collectors","Outlet Volumetric Gas Rate"),
    "Cfuge":       BlockEntry("Centrifuge, high-speed disk","Centrifuges",""),
    "Filter":      BlockEntry("Vacuum drum filter","Filters",""),
    "CfFilter":    BlockEntry("Plate & frame filter","Filters",""),
}

def CreateEquipment(name:str, year:int ,process_type:str, block):
    try:
        conf = EquipmentConfig[block['record_type']]
        new_equip = Equipment(
            name=name,
            param=block['data'][conf.paramater_name][0],
            process_type=process_type,
            category=conf.category, 
            type=conf.type,
            material=block.get('material', "Carbon steel"),
            num_units=1,
            target_year=year, 
        )
        print(f"Added block of type {block['record_type']}")
        return new_equip
    except Exception as err:
        print(f"Could not Automatically add block of type {block['record_type']} Because: {err}, Please add manually if needed.")
        return False


# =====================

def TEA_config(data:dict,
               variable_opex_inputs:VariableOpexInputs,
               plant_products: PlantProducts,
               process_type="Fluids",
               daily_prod=100, # TODO: find a better value for this
               country="Netherlands",
               operator_hourly_rate=38.11,
               interest_rate=0.09,
               project_lifetime="100",
               target_year=2023):
    '''
    Uses the data from aspen (and some additional parameters) to create a TEA plant configuration.
    see TEA documentation for additional configuration options.
    '''
    configuration = dict()

    equip = []
    for block_name in data:
        block = data[block_name]
        new_equip = CreateEquipment(block_name,target_year,process_type, block)
        if new_equip:
            equip.append(new_equip)
        else:
            continue

    configuration['equipment'] = equip
    configuration['process_type'] = process_type 
    configuration['daily_prod'] = daily_prod 
    configuration['country'] = country 


    configuration["variable_opex_inputs"] = variable_opex_inputs
    configuration['operator_hourly_rate'] = operator_hourly_rate 
    configuration['interest_rate'] = interest_rate

    configuration['plant_products'] = plant_products

    configuration["project_lifetime"] = project_lifetime

    return configuration

