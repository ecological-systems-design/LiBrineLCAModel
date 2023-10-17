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

    locations = [("Salton Sea", "Sal"), ("Upper Rhine Valley", "URG")]

    country_location = "US-WECC"

    from rsc.lithium_production.licarbonate_processes import loop_functions

    eff = 0.5
    Li_conc = 0.018
    abbrev_loc = "Sal"
    op_location = "Salton Sea"


    from rsc.lithium_production.creating_inventories import inventories
    demand_all, df = inventories(Li_conc= 0.018, Li_conc_steps = 0.1,  max_eff = 0.5, min_eff = 0.4, eff_steps = 0.1,
                                 max_number_boreholes = 0, borehole_depth = 0, op_location="Salton Sea")