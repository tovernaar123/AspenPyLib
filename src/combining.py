import aspen
from openpytea.plant import Plant
import inout
from os.path import abspath
import sys
from pprint import pprint
#The price information for the different compounds in the aspen simulation file,
#If the price here is not given the price of aspen will be used.
pricesForOpex = {
    'CH4' : 0.1,
    'C' : 0.2,
    'H2' : 0.3,
    'WATER' : 0.4,
    'O2' : 0.5,
    'N2' : 0.6,
    'CO2' : 0.7,
    'NI' : 0.8,
}

#Startup aspen by opening the simulation file
Aspen = aspen.init_aspen(abspath(sys.argv[1]))

#Read-out the required blocks and there data from aspen. 
Blocks = aspen.read_data(Aspen)

#Get all the  streams from aspen.
StreamsForOpex = aspen.GetStreams(Aspen)

#Figure out what streams are input (feed) streams, and how much that feed costs.
opex_d = inout.createOPEXdict(StreamsForOpex, Blocks, pricesForOpex)

#Finally create the config needed for the TEA pacakge
confg = inout.TEA_config(Blocks, opex_d)
#Modify the config if needed.
#create the plant.
plant = Plant(confg)
pprint(confg,indent=4)
#Now use the function from TEA to get the cost.
plant.calculate_levelized_cost(True)
