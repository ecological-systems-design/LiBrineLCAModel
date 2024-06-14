import bw2data as bd
from pathlib import Path
import pandas as pd
# from Processes import *
# from chemical_formulas import *
# from operational_data_salton import *
from src.BW2_calculations.setting_up_bio_and_ei import import_biosphere, import_ecoinvent


import os

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"URG_39"
biosphere = f"biosphere3"
deposit_type = "geothermal"

site_location = site_name[:3]

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}'
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

    locations = [("Salton Sea", "Sal"), ("Upper Rhine Graben", "URG")]

    #bio = bd.Database('biosphere3')
    # water = bd.Database(water_name)
    # site = bd.Database(site_name)
    #ei_reg = bd.Database(ei_name)

    country_location = "DE"

    # print all brightway2 databases
    print(bd.databases)

    # from src.LifeCycleInventoryModel_Li.creating_inventories import inventories
    # demand_all, df = inventories(Li_conc= 0.04, max_eff = 0.9, min_eff = 0.3, eff_steps = 0.1,
    #                             max_number_boreholes = 0, borehole_depth = 0)

    #from src.BW2_calculations.lithium_site_db import check_database

    #site = check_database(database_name=site_name, country_location="US", elec_location="US-WECC",
    #               eff=0.5, Li_conc=0.04, op_location="Salton Sea",
    #               abbrev_loc="Sal", ei_name=ei_name, biosphere=biosphere)

    eff = 0.5
    Li_conc = 0.018
    abbrev_loc = "URG"
    op_location = "Upper Rhine Graben"

    # initialize the processing sequence
    from src.LifeCycleInventoryModel_Li.import_site_parameters import extract_data, update_config_value

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)
    from src.LifeCycleInventoryModel_Li.licarbonate_processes import *

    process_sequence = [
        SiFeRemovalLimestone(),
        MnZn_removal_lime(),
        acidification(),
        Li_adsorption(),
        CaMg_removal_sodiumhydrox(),
        ion_exchange_L(),
        reverse_osmosis(),
        triple_evaporator(),
        Liprec_TG(),
        CentrifugeTG(),
        washing_TG(),
        dissolution(),
        Liprec_BG(),
        CentrifugeBG(),
        washing_BG(),
        CentrifugeWash(),
        rotary_dryer()
        ]

    # 1. Define your initial parameters
    prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc])

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}.txt"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

    # 3. Run the processes
    dataframes_dict = manager.run(filename)



    max_eff = 1.0
    min_eff = 0.5
    eff_steps = 0.1
    Li_conc_steps = 0.005
    Li_conc_max = 0.03
    Li_conc_min = 0.005

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                   min_eff, eff_steps, Li_conc_steps, Li_conc_max, Li_conc_min)

    print(results)



    from src.BW2_calculations.setting_up_db_env import database_environment

    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                             eff, Li_conc, op_location, abbrev_loc, dataframes_dict)

    #from src.BW2_calculations.lci_method_aware import import_aware
    #import_aware(ei_reg, bio)

    #from src.BW2_calculations.lci_method_pm import import_PM
    #import_PM(ei_reg, bio)


    #from src.BW2_calculations.calculating_impacts import  calculate_impacts_for_selected_methods
    #fu = [act for act in site_db if "Geothermal Li" in act['name']]
    #results = calculate_impacts_for_selected_methods(activities=fu, amounts=[1])

    #print(results)

    eff = 0.9
    Li_conc = 0.03

    from src.BW2_calculations.iterating_LCIs import change_exchanges_in_database
    #site_db = change_exchanges_in_database(eff, Li_conc, site_name, abbrev_loc, results)



    #Loop through all activities in the database
    for activity in site_db :
        print("Activity:", activity, activity['type'])
        # Loop through all exchanges for the current activity
        for exchange in activity.exchanges() :
            exchange_type = exchange.get('type', 'Type not specified')
            print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    #method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    #method_PM = [m for m in bd.methods if "PM regionalized" in str(m)][0]

    method_list = [method_cc]

    from src.BW2_calculations.impact_assessment import calculate_impacts_for_selected_scenarios

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, eff_range, Li_conc_range,
                                                       abbrev_loc)

    from src.Postprocessing_results.visualization_functions import Visualization
    # Plot the results
    Visualization.plot_impact_categories(impacts, abbrev_loc)



