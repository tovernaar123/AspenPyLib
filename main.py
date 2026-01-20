import sys
from os.path import abspath

import src.aspen as a

if len(sys.argv) < 2:
    print("Should be called with the name of the aspen file")
    exit(1)

# Connect to Aspen Plus
aspen = a.init_aspen(abspath(sys.argv[1]))
aspen.Visible = True

data = a.read_data(aspen)
streams = a.GetStreams(aspen, vocal=False)

from pprint import pprint

# pprint.pprint(data)
pprint(streams)