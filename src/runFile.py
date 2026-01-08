import aspen
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

DummyData = {"dummy_block":{
        'parameter' : 78, # in this case volume (check when making data)
        'type' : 'Compr',
        'material' : 'Aluminum',
        'input_name': "electricity",
        'input_amount' : 6,
}}

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
pprint(BlocksForOpex)
opex_d = inout.createOPEXdict(StreamsForOpex, BlocksForOpex, pricesForOpex)
pl = inout.TEA_plant(DummyData, TEA_Plant_configuration, opex_d)
pl.calculate_levelized_cost(True)
