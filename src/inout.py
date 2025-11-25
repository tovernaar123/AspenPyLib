"""
functions for making and loading JSONs, and also turning data into TEA things

by: Johannes

p.s: json things are basically just wrappers right now.
"""
import sys
import json
import numpy as np
# someone better versed in python make this pretty
from openpytea.plant import Plant
from openpytea.equipment import *
from openpytea.analysis import *
"""
TODO:
- [] add process plant creation
- [] make actual docstrings 


"""

@dataclass
class SearchBlock:
    data: list[tuple[str, str]]
    children: list[str]

search = {
    "Hierarchy": SearchBlock([], ["Blocks"]),
    "Compr": SearchBlock([("WNET", "Net Power")], []),
    "MCompr": SearchBlock([("WNET", "Net Power")], []),
    "Turb": SearchBlock([("WNET", "Net Power")], []),
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

RECORD_TYPE = 6
def readAspen(aspen, search=search):
    data = {}
    blocks = list(get_all_children(aspen.Application.Tree.FindNode(r"\Data\Blocks")))
    # Loop through all blocks
    for block in blocks:
        recordType = block.AttributeValue(RECORD_TYPE)
        if block.Name[:4] == "TURB":
            recordType = "Turb"
        # print(block.Name, block.Value, block.ValueType, recordType)
        curr_data = {}
        if s := search.get(recordType):
            for path, name in s.data:
                b = block.FindNode(rf"Output\{path}")
                curr_data["parameter"] = np.abs(b.Value)
                curr_data["name"] = name
                curr_data["type"] = recordType
                curr_data["unit"] = b.UnitString
                data[block.Name] = curr_data
            for path in s.children:
                b = block.FindNode(rf"Data\{path}")
                blocks.extend(get_all_children(b))
    return data
# ======== IO ================

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
process_type_d = {
    "Compr" : "Fluids",
    "MCompr" : "Fluids",            # I copy-pasted the Compr attributes somebody please check this
    "Turb" : "Fluids"               # I totally made up this type, there has to be a better way
}
category_d = {
    "Compr" : 'Pumps',          # Lets all pretend compressors are actually pumps
    "MCompr" : 'Pumps',
    "Turb" : 'Turbines'

}
TEA_type_d = {
    'Compr' : 'Centrifugal pump',
    'MCompr' : 'Centrifugal pump',
    'Turb' : 'Steam turbine'
}
opex_d = {
        # For the variable opex inputs, the consumption is always based on daily consumption

        #Wnet + the other power names
        "electricity": {
            "consumption": (1000 + 1000) * 24,
            #wondering of aspen knows these?
            "price": 0.10, 
            "price_std": 0.05 / 2,
            "price_max": 3,
            "price_min": 0.01,
        },

        #Should be taken from the streams
        "refrigerant": {  # 1.5 kg/h taken from Figure 1
            "consumption": 1.5 * 24,
            "price": 5,
            "price_std": 3 / 2,
            "price_max": 10,
            "price_min": 1,
        },

        "cooling_water": {  # 11.03 kg/h taken from Figure 1
            "consumption": 39_690 * 24,
            "price": 2.4592e-4,
            "price_std": 1e-4,
            "price_max": 4e-4,
            "price_min": 1e-5,
        },
}

# ======== utils =========

def add(d:dict, key:str, value)->None:
    '''adds value to key in dictionary or creates it if it doesn't exist'''
    if key in d:
        d[key] += value
    else:
        d[key] = value

# =====================

def TEA_plant(data:dict, configuration:dict):
    '''
    translates the data into the TEA plant.
    see TEA documentation for configuration options.
    some configuration values are automatically overridden based on the data.
    '''

    # we need to overwrite the process_type, equipment, inputs,
    # and i guess plant_utilization?

    equip = []
    opex_inputs = {} # because this isn't stored in the equipment in TEA
    production = {}
    for block_name in data:
        block = data[block_name]

        new_equip = Equipment(
            name=block_name,
            param=block["parameter"],
            process_type=process_type_d[block['type']],
            category= category_d[block['type']], # the type of block category
            type=TEA_type_d[block['type']], # the specific type
            material=block.get('material', "Carbon steel"), # material made out of
            num_units=1, # i assume they're not grouped
            purchased_cost=None, # does Aspen know maybe?
            cost_func= None, # presume aspen doesn't know
            target_year= 2023, # just doing what would be default
        )
        equip.append(new_equip)
        # do something about inputs:
        #add(opex_inputs, block['input_name'], opex_inputs) # something like this?
        add(production, 'count', 1) # might be more complicated than this

    configuration['equipment'] = equip

    #kinda confused what this was supposed to do
    # make opex inputs "verbose"
    # opex_inputs_verbose = {}
    # for in_name in opex_inputs:
    #     in_val = opex_inputs[in_name]
    #     dict_val = opex_d[in_name]
    #     opex_inputs_verbose[in_name] = dict_val

    # configuration['variable_opex_inputs'] = opex_inputs_verbose
    configuration['process_type'] = 'Fluids' # change based on blocks?
    configuration['daily_prod'] = production['count'] # TEMPORARY
    configuration['country'] = 'Netherlands' # User input


    # This is going to need be made from the streams / blocks
    configuration["variable_opex_inputs"] = opex_d
    configuration['operator_hourly_rate'] = 38.11 # User input
    configuration['interest_rate'] = 0.09 # User input

    return Plant(configuration)


def main():
    data = {"dummy_block":{
            'parameter' : 78, # in this case volume (check when making data)
            'type' : 'compr',
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

    pl = TEA_plant(data, configuration)
    pl.calculate_levelized_cost(True)


#if __name__ == "__main__":
 #   main()

