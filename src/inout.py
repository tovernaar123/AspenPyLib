"""
functions for making and loading JSONs, and also turning data into TEA things

by: Johannes

p.s: json things are basically just wrappers right now.
"""
import sys
import json
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

# ==== dictionaries ====

# find process_type, category, etc. from type


def createOPEXdict(streamData:dict, blockDataDict:dict, prices:dict)->dict:
    opexDict = {}

    netPowerConsumption = 0 #in kW!
    for block in blockDataDict.values():
        try:
            netPowerConsumption += block["data"]["Net Power"][0]
        except KeyError:
            pass
    opexDict["electricity"] = {
        "consumption" : netPowerConsumption * 24,
        "price" : 7.5 #per kWh! TODO what is the real price?
    }
    
    for stream in list(streamData.keys()):
        streamName = stream.split(r"\\")[-1]
        cost = streamData[rf"{stream}"]["SOURCE"]["cost/h"]
        if cost != 0:
            consumption = 0
            for flowrates in list(streamData[rf"{stream}"]["MASSFLOW"][r"\MIXED"].keys()):
                consumption += streamData[rf"{stream}"]["MASSFLOW"][r"\MIXED"][rf"{flowrates}"]
            opexDict[rf"{streamName}"] = {}
            opexDict[rf"{streamName}"]["consumption"] = consumption * 24 #DAILY
            opexDict[rf"{streamName}"]["price"] = cost / consumption #was hourly, now PER UNIT
        else:
            for subsName in list(streamData[rf"{stream}"]["MASSFLOW"][r"\MIXED"].keys()):
                if subsName not in opexDict:
                    opexDict[subsName] = {
                        "consumption": 0,
                        "price": 0
                    }

                opexDict[rf"{subsName}"]["consumption"] += (streamData[rf"{stream}"]["MASSFLOW"][r"\MIXED"][rf"{subsName}"] * 24) #DAILY
                if rf"{subsName}" in prices:
                    opexDict[rf"{subsName}"]["price"] =  prices[rf"{subsName}"]
                else:
                    sys.exit(rf"No given price for {subsName}")
        
    return opexDict
    

### TESTING PURPOSES ###
# from os.path import abspath
# ASPEN = asp.init_aspen(abspath(sys.argv[1]))
# testdict = {}
# testdict = asp.GetStreams(ASPEN)
# blockData = asp.read_data(ASPEN)
# print(createOPEXdict(testdict, blockData))


# ======== utils =========

def add(d:dict, key:str, value)->None:
    '''adds value to key in dictionary or creates it if it doesn't exist'''
    if key in d:
        d[key] += value
    else:
        d[key] = value



# type EquipCategory = Literal[

# ]

# type EquiptType = Literal[

# ]




@dataclass
class BlockEntry:
    type: str
    category: str
    paramater_name:str


EquipmentConfig: dict[str, BlockEntry] = {



    "Mixer":       BlockEntry("Static mixer", "Agitators & mixers", "flow"), 

    "Flash2":      BlockEntry("Vertical CS", "Pressure vessels", "Outlet Pressure"), 
    "Flash3":      BlockEntry("Vertical CS", "Pressure vessels", "Outlet Pressure"), 
    "Decanter":    BlockEntry("Horizontal CS", "Pressure vessels", "flow"), 
    "Sep":         BlockEntry("Vertical CS", "Pressure vessels", "flow"), 
    "Sep2":        BlockEntry("Vertical CS", "Pressure vessels", "flow"),

    "Heater":      BlockEntry("Furnace, cylindrical", "Boilers & Furnaces", "Heating Duty"),
    "HeatX":       BlockEntry("U-tube shell & tube", "Heat exchangers", "Heat Transfer Area"), 
    "MHeatX":      BlockEntry("U-tube shell & tube", "Heat exchangers", "Heat Transfer Area"),
    "RYield":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),
    "REquil":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),   
    "RGibbs":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),
    "RCSTR":       BlockEntry("Jacketed agitated",  "Reactors", "Volume"),
    "RYield":      BlockEntry("Jacketed agitated",  "Reactors", "Volume"),


    "Pump":        BlockEntry("Single-stage centrifugal pump","Pumps","Volumetric Flow"),
    "Compr":       BlockEntry("Compressor, centrifugal","Compressors & Blowers","Net Power"),
    "MCompr":       BlockEntry("Compressor, centrifugal","Compressors & Blowers","Net Power"),
    "Crytallizer": BlockEntry("Scraped surface crystallizer","Crystallizers",""),
    "Crusher":     BlockEntry("Pulverizer","Crushers",""),
    "Dryer":       BlockEntry("Direct contact rotary dryer","Dryers",""),
    "Fluidbed":    BlockEntry("Indirect fluidized-bed","Reactors",""),
    "Cyclone":     BlockEntry("Gas multi-cyclone","Cyclones","Outlet Volumetric Gas Rate"),
    "Cfuge":       BlockEntry("Centrifuge, high-speed disk","Centrifuges",""),
    "Filter":      BlockEntry("Vacuum drum filter","Filters",""),
    "CfFilter":    BlockEntry("Plate & frame filter","Filters",""),

    #TODO figure out how to parse columns
    # "DSTWU": BlockEntry("Fluids", "Furnace, cylindrical", "Boilers & Furnaces"), 
    # "Distl": BlockEntry("Fluids", "Furnace, cylindrical", "Boilers & Furnaces"), 
    # "SCFrac": BlockEntry("Fluids", "Furnace, cylindrical", "Boilers & Furnaces"), 
    # "RadFrac": BlockEntry("Fluids", "Furnace, cylindrical", "Boilers & Furnaces"), 
    # "MultiFrac": BlockEntry("Fluids", "Furnace, cylindrical", "Boilers & Furnaces"), 
    # "PetroFrac": BlockEntry("Fluids", "Furnace, cylindrical", "Boilers & Furnaces"), 
    # "RateFrac": BlockEntry("Fluids", "Furnace, cylindrical", "Boilers & Furnaces"), 

}

def CreateEquipment(name:str, year:int ,process_type:str, block):
    try:
        conf = EquipmentConfig[block['record_type']]
        new_equip = Equipment(
            name=name,
            param=block['data'][conf.paramater_name][0],
            process_type=process_type,
            category=conf.category, # the type of block category
            type=conf.type, # the specific type
            material=block.get('material', "Carbon steel"), # material made out of
            num_units=1, # i assume they're not grouped
            target_year=year, # just doing what would be default
        )
        print(f"Added block of type {block['record_type']}")
        return new_equip
    except Exception as err:
        print(f"Could not Automatically add block of type {block['record_type']} Because: {err}, Please add manually if needed.")
        return False


# =====================

def TEA_config(data:dict, variable_opex_inputs:dict,
               process_type="Fluids",
               daily_prod=100,  # TODO: find a better value for this
               country="Netherlands",
               operator_hourly_rate=38.11,
               interest_rate=0.09,
               project_lifetime="100",
               target_year=2023):
    '''
    Uses the data from aspen (and some additional parameters) to create a TEA plant configuration.
    see TEA documentation for additional configuration options.
    '''

    # we need to overwrite the process_type, equipment, inputs,
    # and i guess plant_utilization?
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
    configuration['process_type'] = process_type # change based on blocks?
    configuration['daily_prod'] = daily_prod # TEMPORARY
    configuration['country'] = country # User input


    # This is going to need be made from the streams / blocks
    configuration["variable_opex_inputs"] = variable_opex_inputs #variable opexDict
    configuration['operator_hourly_rate'] = operator_hourly_rate # User input
    configuration['interest_rate'] = interest_rate # User input

    configuration["project_lifetime"] = project_lifetime

    return configuration


def main():
    data = {"dummy_block":{
            'parameter' : 78, # in this case volume (check when making data)
            'type' : 'Compr',
            'material' : 'Aluminum',
            'input_name': "electricity",
            'input_amount' : 6,
    }}
    configuration = {
        "plant_name" : "test_plant",
        'country': 'Netherlands',
        'region': None,
        'interest_rate': 0.09,
        'operator_hourly_rate': 38.11,
        'project_lifetime': 20, # Taken from case study 1
        'plant_utilization': 0.95,
    }

    pl_conf = TEA_config(data)
    pl_conf["plant_name"] = "test_plant"
    print(pl_conf)
    pl = Plant(pl_conf)
    pl.calculate_levelized_cost(True)


if __name__ == "__main__":
   main()

