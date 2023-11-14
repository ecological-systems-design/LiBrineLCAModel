import bw2data as bd
from pathlib import Path
import numpy as np
import pickle
from rsc.visualizations_LCI_and_BW2.visualization_functions import Visualization
import pandas as pd
# from Processes import *
# from chemical_formulas import *
# from operational_data_salton import *
from rsc.Brightway2.setting_up_bio_and_ei import import_biosphere, import_ecoinvent


import os

if not os.path.exists("results") :
    os.mkdir("results")

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

name_list = ['df_SiFe_removal_limestone', 'df_MnZn_removal_lime', 'df_acidification', 'df_Li_adsorption',
             'df_CaMg_removal_sodiumhydrox', 'df_ion_exchange_L', 'df_reverse_osmosis', 'df_triple_evaporator',
             'df_Liprec_TG', 'df_centrifuge_TG', 'df_washing_TG', 'df_dissolution', 'df_Liprec_BG',
             'df_centrifuge_BG',
             'df_washing_BG', 'df_centrifuge_wash', 'df_rotary'
             ]

# Biosphere
if __name__ == '__main__' :

    locations = [("Salton Sea", "Sal"), ("Upper Rhine Valley", "URG")]

    country_location = "US-WECC"

    eff = 0.5
    Li_conc = 0.018
    abbrev_loc = "Sal"
    op_location = "Salton Sea"

    # initialize the processing sequence
    from rsc.lithium_production.import_site_parameters import extract_data, update_config_value

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)
    print(initial_data)

    op_location = "Upper Rhine Graben"
    abbrev_loc = "URG"
    Li_conc = 0.019
    initial_data_1 = extract_data(op_location, abbrev_loc, Li_conc)
    print(initial_data_1)







