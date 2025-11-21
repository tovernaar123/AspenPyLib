"""
functions for making and loading JSONs, and also turning data into TEA things

by: Johannes

ps: json things are basically just wrappers right now.
"""
import sys
import json
import sys # someone better versed in python make this pretty

from openpytea.plant import Plant
"""
TODO:
- [] add process plant creation
- [] make actual docstrings 


"""

def write_JSON(data, path)->None:
    """
    saves to the given file path, also formats the data (if necessary)
    """
    # make this a method if we make the data into objects

    # format data here

    with open(path, "w") as file:
        json.dump(data, file)

def read_JSON(path)->dict:
    """
    inverse of the other thing, also un-formats the data (if neccessary)
    """

    with open(path, "r") as file:
        data = json.load(file)
    
    # unformat data here

    return data


def TEA_plant(data:dict, configuration:dict):
    '''
    translates the data into the TEA plant.
    see TEA documentation for configuration options
    '''

    pl = plant.Plant(configuration)

    raise NotImplementedError("I'm not finished yet...")


def main():
    data = {"foo":"bar"}

    TEA_plant({},{})


if __name__ == "__main__":
    main()

