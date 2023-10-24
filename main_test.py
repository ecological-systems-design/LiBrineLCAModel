import bw2data as bd
from pathlib import Path
import numpy as np
import pickle
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
    eff_range = np.arange(max_eff, min_eff - eff_steps + 0.001, -eff_steps)

    Li_conc_range = [Li_conc_max]
    while Li_conc_range[-1] > Li_conc_min :
        next_value = Li_conc_range[-1] - Li_conc_steps
        if next_value < 0 :
            break
        elif next_value < Li_conc_min :
            next_value = Li_conc_min
        Li_conc_range.append(next_value)

    Li_conc_range = np.array(Li_conc_range)

    # Dictionary to store results
    results_dict = {}

    for eff in eff_range :
        results_dict[eff] = {}
        for Li in Li_conc_range :
            filename = f"{abbrev_loc}_eff{eff}_Li{Li}.txt"
            print(filename)
            # Update the initial_data with new Li_conc value
            initial_data = extract_data(op_location, abbrev_loc, Li)
            print(Li)
            print(eff)

            # Define your initial parameters
            prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc])

            # Initialize the ProcessManager
            manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

            # Run the processes
            result_df = manager.run(filename)


            # Calculate resources per production mass
            energy_per_prod_mass, elec_per_prod_mass, water_per_prod_mass = manager.calculate_resource_per_prod_mass(result_df, prod)

            # Store the calculated values in your results dictionary or another data structure
            results_dict[eff][Li] = {
                'data_frames' : result_df,
                'resources_per_kg': (energy_per_prod_mass, elec_per_prod_mass, water_per_prod_mass)
                }

    # Save the dictionary
    with open(f"results_dict_{abbrev_loc}_{Li}_{eff}.pkl", "wb") as f :
        pickle.dump(results_dict, f)

    print("Simulation completed and results stored in the dictionary.")

    print(results_dict)

    from rsc.visualizations_LCI_and_BW2.visualization_functions import *

    # Assuming manager is an instance of ProcessManager and results_dict is your results data
    viz = Visualization()
    viz.plot_resources_per_kg(results_dict, abbrev_loc)

    # 2. Load the dictionary


    # 5. Plot the results
    import plotly_express as px
    import plotly.graph_objects as go





