import bw2data as bd
from pathlib import Path
from src.LifeCycleInventoryModel_Li.import_site_parameters import extract_data,update_config_value
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
from src.BW2_calculations.setting_up_db_env import *
from src.BW2_calculations.lci_method_aware import import_aware
from src.BW2_calculations.impact_assessment import calculate_impacts_for_selected_scenarios
from src.BW2_calculations.impact_assessment import saving_LCA_results,print_recursive_calculation
from src.Postprocessing_results.visualization_functions import Visualization

import os

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"East Taijinar"
biosphere = f"biosphere3"
deposit_type = "salar"

site_location = site_name[:3]

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_quicklime'
    bd.projects.set_current(project)
    print(project)

    #del bd.databases[site_name]
    #del bd.databases[ei_name]

    country_location = "CN-NWG"

    # print all brightway2 databases
    print(bd.databases)

    eff = 0.35
    Li_conc = 0.012
    abbrev_loc = "EaTai"
    op_location = site_name

    # initialize the processing sequence

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)

    process_sequence = [
        evaporation_ponds(),
        Mg_removal_quicklime(),
        CentrifugeQuicklime(DEFAULT_CONSTANTS,{}),
        sulfate_removal_calciumchloride(),
        acidification(),
        Li_adsorption(),
        ion_exchange_L(),
        Electrodialysis(),
        reverse_osmosis(),
        Liprec_TG(),
        CentrifugeTG(DEFAULT_CONSTANTS,{}),
        washing_TG(),
        dissolution(),
        Liprec_BG(),
        CentrifugeBG(DEFAULT_CONSTANTS,{}),
        washing_BG(),
        CentrifugeWash(DEFAULT_CONSTANTS,{}),
        rotary_dryer()
        ]

    # 1. Define your initial parameters
    prod,m_pumpbr = setup_site(eff,site_parameters=initial_data[abbrev_loc],constants=DEFAULT_CONSTANTS)

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc],m_pumpbr,prod,process_sequence,filename,DEFAULT_CONSTANTS,
                             params={})

    # 3. Run the processes
    dataframes_dict = manager.run(filename)

    max_eff = 0.9
    min_eff = 0.2
    eff_steps = 0.1
    Li_conc_steps = 0.02
    Li_conc_max = 0.192
    Li_conc_min = 0.012

    results,eff_range,Li_conc_range = manager.run_simulation(op_location,abbrev_loc,process_sequence,max_eff,
                                                             min_eff,eff_steps,Li_conc_steps,Li_conc_max,
                                                             Li_conc_min,DEFAULT_CONSTANTS,params=None)

    print(results)

    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                eff, Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map)


    import_aware(ei_reg, bio, site_name, site_db,copy_site_db = None)

    # from src.BW2_calculations.lci_method_pm import import_PM

    # import_PM(ei_reg, bio, site_name, site_db)

    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    # method_PM = [m for m in bd.methods if "PM regionalized" in str(m)][0]
    # print(method_PM)

    method_list = [method_cc, method_water]

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, abbrev_loc, eff_range, Li_conc_range,
                                                       literature_eff=None, literature_Li_conc=None)
    # print(impacts)

    # saving results

    saving_LCA_results(impacts, abbrev_loc)

    # Plot the results
    Visualization.plot_impact_categories(impacts, abbrev_loc)
