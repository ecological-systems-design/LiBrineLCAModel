import bw2data as bd
from pathlib import Path

import os

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Silver Peak"
biosphere = f"biosphere3"
deposit_type = "salar"

site_location = site_name[:3]

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_5'
    bd.projects.set_current(project)
    print(project)

    #del bd.databases[site_name]
    #del bd.databases[ei_name]

    country_location = "US-WECC"

    # print all brightway2 databases
    print(bd.databases)

    eff = 0.51
    Li_conc = 0.02
    abbrev_loc = "Sil"
    op_location = "Silver Peak"

    # initialize the processing sequence
    from rsc.lithium_production.import_site_parameters import extract_data, update_config_value

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)
    from rsc.lithium_production.licarbonate_processes import *

    process_sequence = [
        evaporation_ponds(),
        Centrifuge_general(),
        Liprec_TG(),
        washing_TG(),
        CentrifugeTG(),
        dissolution(),
        Centrifuge_general(),
        ion_exchange_H(custom_name = None),
        ion_exchange_H(custom_name = "df_ion_exchange_H_second"),
        ion_exchange_L(),
        Liprec_BG(),
        CentrifugeBG(),
        washing_BG(),
        CentrifugeWash(),
        rotary_dryer()
        ]

    # 1. Define your initial parameters
    prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc])

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

    # 3. Run the processes
    dataframes_dict = manager.run(filename)

    max_eff = 0.5
    min_eff = 0.3
    eff_steps = 0.2
    Li_conc_steps = 0.01
    Li_conc_max = 0.02
    Li_conc_min = 0.01

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                                                               min_eff, eff_steps, Li_conc_steps, Li_conc_max,
                                                               Li_conc_min)

    print(results)

    from rsc.Brightway2.setting_up_db_env import *

    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                eff, Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map)

    from rsc.Brightway2.lci_method_aware import import_aware

    import_aware(ei_reg, bio, site_name, site_db)

    # from rsc.Brightway2.lci_method_pm import import_PM

    # import_PM(ei_reg, bio, site_name, site_db)

    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    # method_PM = [m for m in bd.methods if "PM regionalized" in str(m)][0]
    # print(method_PM)

    method_list = [method_cc, method_water]

    from rsc.Brightway2.impact_assessment import calculate_impacts_for_selected_scenarios

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, abbrev_loc, eff_range, Li_conc_range,
                                                       literature_eff=None, literature_Li_conc=None)
    # print(impacts)

    # saving results
    from rsc.Brightway2.impact_assessment import saving_LCA_results, print_recursive_calculation

    saving_LCA_results(impacts, abbrev_loc)

    from rsc.Postprocessing_results.visualization_functions import Visualization

    # Plot the results
    Visualization.plot_impact_categories(impacts, abbrev_loc)
