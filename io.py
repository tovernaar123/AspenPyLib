"""
functions for making and loading JSONs, and also turning data into TEA things

by: Johannes

p.s: json things are basically just wrappers right now.
"""
import sys
import json
# someone better versed in python make this pretty
from openpytea.plant import *
from openpytea.equipment import *
from openpytea.analysis import *
"""
TODO:
- [] add process plant creation
- [] make actual docstrings 


"""

# ======== IO ================

def write_JSON(data, path)->None:
    """
    saves to the given file path, also formats the data (if necessary)
    """
    # make this a method if we make the data into objects

    # format data here (nothing currently)

    with open(path, "w") as file:
        json.dump(data, file)

def read_JSON(path)->dict:
    """
    inverse of the other thing, also un-formats the data (if neccessary)
    """

    with open(path, "r") as file:
        data = json.load(file)
    
    # unformat data here (nothing currently)

    return data

# ==== dictionaries ====

# find process_type, category, etc. from type
process_type_d = {
    "compr" : "Fluids",
}
category_d = {
    "compr" : 'Compressors & blowers' ,
}
TEA_type_d = {
    'compr' : 'Compressor, centrifugal',
}
opex_d = { # TODO: make way for user editing later on
    'electricity': {
        'price': 0.10, 'price_std': 0.05/2, 'price_max': 3, 'price_min': 0.01
    },
    'refrigerant': { 
        'price': 5, 'price_std': 3/2, 'price_max': 10, 'price_min': 1
    },
    'cooling_water':{
        'price': 2.4592e-4, 'price_std': 1e-4, 'price_max': 4e-4, 'price_min': 1e-5
    }
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
            material=block['material'], # material made out of
            num_units=1, # i assume they're not grouped
            purchased_cost=None, # does Aspen know maybe?
            cost_func= None, # presume aspen doesn't know
            target_year= 2023 # just doing what would be default
        )
        equip.append(new_equip)
        # do something about inputs:
        add(opex_inputs, block['input_name'], opex_inputs) # something like this?
        add(production, 'count', 1) # might be more complicated than this

    configuration['equipment'] = equip

    # make opex inputs "verbose"
    opex_inputs_verbose = {}
    for in_name in opex_inputs:
        in_val = opex_inputs[in_name]
        dict_val = opex_d[in_name]
        opex_inputs_verbose[in_name] = dict_val

    configuration['variable_opex_inputs'] = opex_inputs_verbose
    configuration['process_type'] = 'Fluids' # change based on blocks?
    configuration['daily_prod'] = production['count'] # TEMPORARY

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
        'country': 'Netherlands', 'region': None,
        'interest_rate': 0.09,
        'operator_hourly_rate': 38.11,
        'project_lifetime': 20, # Taken from case study 1
        'plant_utilization': 0.95,
    }

    pl = TEA_plant(data, configuration)
    pl.calculate_levelized_cost(True)


if __name__ == "__main__":
    main()

