import sys
from os.path import abspath

from src.aspen import init_aspen, read_data

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

# Connect to Aspen Plus
aspen = init_aspen(abspath(sys.argv[1]))

data = read_data(aspen)

import pprint

pprint.pprint(data)