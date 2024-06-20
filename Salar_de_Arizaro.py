import bw2data as bd
from pathlib import Path
from src.BW2_calculations.setting_up_db_env import *
from src.BW2_calculations.lci_method_aware import import_aware
from src.BW2_calculations.impact_assessment import calculate_impacts_for_selected_scenarios, calculate_impacts_for_sensitivity_analysis
from src.BW2_calculations.impact_assessment import saving_LCA_results,print_recursive_calculation, saving_sensitivity_results
from src.LifeCycleInventoryModel_Li.operational_and_environmental_constants import DEFAULT_CONSTANTS, SENSITIVITY_RANGES
from src.LifeCycleInventoryModel_Li.import_site_parameters import extract_data, update_config_value
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
import os
import json

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salar de Arizaro"
biosphere = f"biosphere3"
deposit_type = "salar"

site_location = "Ari"

# Biosphere
if __name__ == '__main__':

    project = f'Site_{site_name}_7'

    project = "default"
    #Create a list with the site_name and "Site_{site_name}_number"; numbers should go from 1 to 25
    for i in range(1,6):
        project_old = f'Site_{site_name}_{i}'
        if project_old in bd.projects:
            print(f'Project {project_old} exists')
            bd.projects.delete_project(project_old,delete_dir=True)
            bd.projects.set_current(project)
        else:
            print(f'Project {project_old} does not exist')

    project = f'Site_{site_name}_7'

    bd.projects.set_current(project)
    print(project)

    #del bd.databases[site_name]
    #del bd.databases[ei_name]

    country_location = "AR"

    # print all brightway2 databases
    print(bd.databases)

    eff = 0.77
    Li_conc = 0.01
    abbrev_loc = "Ari"
    op_location = "Salar de Arizaro"

    # initialize the processing sequence

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)


    process_sequence = [
        evaporation_ponds(),
        Li_adsorption(),
        triple_evaporator(),
        ion_exchange_L(),
        DLE_evaporation_ponds(),
        Liprec_TG(),
        CentrifugeTG(DEFAULT_CONSTANTS, SENSITIVITY_RANGES),
        washing_TG(),
        dissolution(),
        Liprec_BG(),
        CentrifugeBG(DEFAULT_CONSTANTS, SENSITIVITY_RANGES),
        washing_BG(),
        CentrifugeWash(DEFAULT_CONSTANTS, SENSITIVITY_RANGES),
        rotary_dryer()
    ]

    # 1. Define your initial parameters
    prod, m_pumpbr = setup_site(eff, initial_data[abbrev_loc], DEFAULT_CONSTANTS)

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename, DEFAULT_CONSTANTS, params={})

    # 3. Run the processes
    dataframes_dict = manager.run(filename)

    max_eff = 0.77
    min_eff = 0.5
    eff_steps = 0.3
    Li_conc_steps = 0.02
    Li_conc_max = 0.026065574
    Li_conc_min = 0.026065574

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                                                               min_eff, eff_steps, Li_conc_steps, Li_conc_max,
                                                               Li_conc_min, DEFAULT_CONSTANTS, params=None)

    print(results)

    # 4. Run the sensitivity analysis
    #manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename, DEFAULT_CONSTANTS, params={})

    eff = 0.77
    #sensitivity_results = manager.run_sensitivity_analysis(filename, op_location, abbrev_loc, Li_conc, eff)



    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                eff, Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map)


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

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]

    # # 4. Run the sensitivity analysis
    # manager = ProcessManager(initial_data[abbrev_loc],m_pumpbr,prod,process_sequence,filename,DEFAULT_CONSTANTS,
    #                          params={})
    #
    # eff = 0.77
    # sensitivity_results = manager.run_sensitivity_analysis(filename,op_location,abbrev_loc,Li_conc,eff)
    #
    # sensitivity_impacts = calculate_impacts_for_sensitivity_analysis(activity, method_list, sensitivity_results, site_name, ei_name, abbrev_loc)
    #
    #
    # saving_sensitivity_results(sensitivity_impacts, abbrev_loc, save_dir= r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\sensitivity_results')

    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, abbrev_loc, eff_range, Li_conc_range,
                                                        literature_eff=None, literature_Li_conc=None)
    #print(impacts)

    # saving results

    saving_LCA_results(impacts, abbrev_loc)

