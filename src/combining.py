import aspen
from openpytea.plant import Plant
import inout
from os.path import abspath
import sys
from pprint import pprint

TEA_Plant_configuration = {
    "plant_name" : "test_plant",
    'country': 'Netherlands',
    'region': None,
    'interest_rate': 0.09,
    'operator_hourly_rate': 38.11,
    'project_lifetime': 20, # Taken from case study 1
    'plant_utilization': 0.95,
}


#prices per unit for substances:
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

Aspen = aspen.init_aspen(abspath(sys.argv[1]))
StreamsForOpex = aspen.GetStreams(Aspen)
BlocksForOpex = aspen.read_data(Aspen)
opex_d = inout.createOPEXdict(StreamsForOpex, BlocksForOpex, pricesForOpex)
confg = inout.TEA_config(BlocksForOpex, opex_d)

plant = Plant(confg)
pprint(confg,indent=4)
plant.calculate_levelized_cost(True)
