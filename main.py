import bw2data as bd
from pathlib import Path
import pandas as pd
# from Processes import *
# from chemical_formulas import *
# from operational_data_salton import *
from rsc.Brightway2.set_up_bw2 import import_biosphere
from rsc.Brightway2.import_db import import_ecoinvent

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

site_location = site_name[:3]

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_7'
    bd.projects.set_current(project)
    print(project)

    if biosphere not in bd.databases :
        import_biosphere(biosphere)
    else :
        print(f"{biosphere} database already exists!!! No import is needed")

    if ei_name not in bd.databases :
        import_ecoinvent(ei_path, ei_name)
    else :
        print(f"{ei_name} database already exists!!! No import is needed")

    locations = [("Salton Sea", "Sal"), ("Upper Rhine Valley", "URG")]

    bio = bd.Database('biosphere3')
    # water = bd.Database(water_name)
    # site = bd.Database(site_name)
    ei_reg = bd.Database(ei_name)

    country_location = "US-WECC"

    from rsc.lithium_production.processes import loop_functions

    eff = 0.5
    Li_conc = 0.04
    abbrev_loc = "Sal"
    location = "Salton Sea"
    loop_functions(eff, Li_conc, op_location=location, abbrev_loc=abbrev_loc)

    # print all brightway2 databases
    print(bd.databases)

    # from rsc.lithium_production.creating_inventories import inventories
    # demand_all, df = inventories(Li_conc= 0.04, max_eff = 0.9, min_eff = 0.3, eff_steps = 0.1,
    #                             max_number_boreholes = 0, borehole_depth = 0)

    from rsc.Brightway2.lithium_site_db import check_database

    check_database(database_name=site_name, country_location="US", elec_location="US-WECC",
                   eff=0.5, Li_conc=0.04, op_location="Salton Sea",
                   abbrev_loc="Sal", ei_name=ei_name, biosphere=biosphere)
