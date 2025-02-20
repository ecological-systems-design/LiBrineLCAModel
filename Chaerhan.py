import bw2data as bd
from pathlib import Path
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *

import os

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Chaerhan"
biosphere = f"biosphere3"
deposit_type = "salar"

site_location = "Chaer"

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_5'
    bd.projects.set_current(project)
    print(project)

    #del bd.databases[site_name]
    #del bd.databases[ei_name]

    country_location = "CN-NWG"

    # print all brightway2 databases
    print(bd.databases)

    eff = 0.77
    Li_conc = 0.022
    abbrev_loc = "Chaer"
    op_location = "Chaerhan"

    # initialize the processing sequence
    from src.LifeCycleInventoryModel_Li.import_site_parameters import extract_data, update_config_value

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)

    process_sequence = [
        evaporation_ponds(),
        Li_adsorption(),
        ion_exchange_L(custom_name=None),
        nanofiltration(),
        reverse_osmosis(),
        DLE_evaporation_ponds(),
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

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

    # 3. Run the processes
    dataframes_dict = manager.run(filename)

    max_eff = 0.77
    min_eff = 0.77
    eff_steps = 0.01
    Li_conc_steps = 0.03
    Li_conc_max = 0.022
    Li_conc_min = 0.01

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                                                               min_eff, eff_steps, Li_conc_steps, Li_conc_max,
                                                               Li_conc_min)

    print(results)

    from src.BW2_calculations.lci_setting_up_all_db import *

    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                eff, Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map)

    from src.BW2_calculations.lcia_method_waterscarcity import import_aware

    import_aware(ei_reg, bio, site_name, site_db)

    #from src.BW2_calculations.lci_method_pm import import_PM

    #import_PM(ei_reg, bio, site_name, site_db)

    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    #method_PM = [m for m in bd.methods if "PM regionalized" in str(m)][0]
    # print(method_PM)

    method_list = [method_cc, method_water]

    from src.BW2_calculations.lcia_impact_assessment import calculate_impacts_for_selected_scenarios

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, abbrev_loc, eff_range, Li_conc_range,
                                                        literature_eff=None, literature_Li_conc=None)
    #print(impacts)

    # saving results
    from src.BW2_calculations.lcia_impact_assessment import saving_LCA_results, print_recursive_calculation

    saving_LCA_results(impacts, abbrev_loc)





