import bw2data as bd
from pathlib import Path


import os

if not os.path.exists("../results") :
    os.mkdir("../results")

# Databases
ei_path = Path('../data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salar de Atacama"
biosphere = f"biosphere3"
deposit_type = "salar"

site_location = "Ata"

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_TEST2'
    bd.projects.set_current(project)
    print(project)

    del bd.databases[site_name]
    #del bd.databases[ei_name]


    country_location = "CL"

    # print all brightway2 databases
    print(bd.databases)



    eff = 0.45
    Li_conc = 0.15
    abbrev_loc = "Ata"
    op_location = "Salar de Atacama"

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

    max_eff = 0.45
    min_eff = 0.45
    eff_steps = 0.1
    Li_conc_steps = 0.01
    Li_conc_max = 0.15
    Li_conc_min = 0.15

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                   min_eff, eff_steps, Li_conc_steps, Li_conc_max, Li_conc_min)

    print(results)


    from src.BW2_calculations.setting_up_db_env import *

    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                             eff, Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map)

    from src.BW2_calculations.lci_method_aware import import_aware
    import_aware(ei_reg, bio, site_name)

    #from src.BW2_calculations.lci_method_pm import import_PM
    #import_PM(ei_reg, bio)


    #print(results)


    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    method_list = [method_cc, method_water]

    from src.BW2_calculations.impact_assessment import calculate_impacts_for_selected_scenarios, print_recursive_calculation

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, abbrev_loc,
                                                       eff_range, Li_conc_range)
    print(impacts)

    #saving results
    from src.BW2_calculations.impact_assessment import saving_LCA_results
    saving_LCA_results(impacts, filename, abbrev_loc)


    from src.Postprocessing_results.visualization_functions import Visualization
    # Plot the results
    Visualization.plot_impact_categories(impacts, abbrev_loc)

    rounded_Li = round(Li_conc, 3)

    file_names = [f"{site_name}" + "_climatechange_" + f"{rounded_Li}",
                  f"{site_name}" + "_waterscarcity_" + f"{rounded_Li}"]

    method_list = [method_cc, method_water]

    for method, file_name in zip(method_list, file_names) :
        results_df = print_recursive_calculation(activity, method, abbrev_loc, file_name, max_level=30, cutoff=0.001)
        print(f"Performed recursive calculation for {method} and saved results to {file_name}")

    print(results_df)
