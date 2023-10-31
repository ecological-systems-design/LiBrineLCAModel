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
    from rsc.lithium_production.operational_data_salton import extract_data, update_config_value

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)
    from rsc.lithium_production.licarbonate_processes import *

    process_sequence = [
        SiFe_removal_limestone(),
        MnZn_removal_lime(),
        acidification(),
        Li_adsorption(),
        CaMg_removal_sodiumhydrox(),
        ion_exchange_L(),
        reverse_osmosis(),
        triple_evaporator(),
        Liprec_TG(),
        centrifuge_TG(),
        washing_TG(),
        dissolution(),
        Liprec_BG(),
        centrifuge_BG(),
        washing_BG(),
        centrifuge_wash(),
        rotary_dryer()
        ]

    # 1. Define your initial parameters
    prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc])

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}.txt"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

    # 3. Run the processes
    results = manager.run(filename)

    print(results)

    # 4. Examine the results
    for process_name, dataframe in results.items() :
        print(f"Results for {process_name}:")
        print(dataframe)
        print("\n---\n")

    # 1. Define your initial parameters
    max_eff = 0.9
    min_eff = 0.5
    eff_steps = 0.1
    Li_conc_steps = 0.001
    Li_conc_max = 0.03
    Li_conc_min = 0.001

    #manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
    #                   min_eff, eff_steps, Li_conc_steps, Li_conc_max, Li_conc_min)







