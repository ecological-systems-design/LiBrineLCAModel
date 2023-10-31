import bw2data as bd
from pathlib import Path
import pandas as pd
# from Processes import *
# from chemical_formulas import *
# from operational_data_salton import *
from rsc.Brightway2.setting_up_bio_and_ei import import_biosphere, import_ecoinvent


import os

if not os.path.exists("images") :
    os.mkdir("images")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salton_39"
site_path = f'../../Python/Brightway/Geothermal_brines/Salton_Sea_39.xlsx'
water_name = f"Water_39"
water_path = f'../../Python/Brightway/Geothermal_brines/Water_39.xlsx'
biosphere = f"biosphere3"
deposit_type = "geothermal"

site_location = site_name[:3]

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_47'
    bd.projects.set_current(project)
    print(project)

    #del bd.databases[site_name]
    #del bd.databases[ei_name]


    #if biosphere not in bd.databases :
    #    import_biosphere(biosphere)
    #else :
    #    print(f"{biosphere} database already exists!!! No import is needed")

    #if ei_name not in bd.databases :
    #    import_ecoinvent(ei_path, ei_name)
    #else :
    #    print(f"{ei_name} database already exists!!! No import is needed")

    locations = [("Salton Sea", "Sal"), ("Upper Rhine Valley", "URG")]

    bio = bd.Database('biosphere3')
    # water = bd.Database(water_name)
    # site = bd.Database(site_name)
    ei_reg = bd.Database(ei_name)

    country_location = "US-WECC"

    act = [act for act in ei_reg if act['name'] == 'market for electricity, medium voltage'][0]
    print(act)
    print(f'Adapted {act, act["type"]}')
    for exchange in act.exchanges() :
        exchange_type = exchange.get('type', 'Type not specified')
        print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)