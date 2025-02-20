
from pathlib import Path
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
import bw2data as bd
from src.LifeCycleInventoryModel_Li.import_site_parameters import extract_data, update_config_value
from src.BW2_calculations.lci_setting_up_all_db import *
from src.BW2_calculations.lcia_method_waterscarcity import import_aware
from src.BW2_calculations.lcia_method_pmhealth import import_PM
from src.BW2_calculations.lcia_impact_assessment import calculate_impacts_for_selected_scenarios, calculate_impacts_for_sensitivity_analysis
from src.BW2_calculations.lcia_impact_assessment import saving_sensitivity_results
from src.BW2_calculations.lcia_impact_assessment import saving_LCA_results, print_recursive_calculation, calculate_battery_impacts,save_battery_results_to_csv
from src.LifeCycleInventoryModel_Li.operational_and_environmental_constants import DEFAULT_CONSTANTS, SENSITIVITY_RANGES
import os

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salton"
site_path = f'../../Python/Brightway/Geothermal_brines/Salton_Sea_39.xlsx'
water_name = f"Water_39"
water_path = f'../../Python/Brightway/Geothermal_brines/Water_39.xlsx'
biosphere = f"biosphere3"
deposit_type = "geothermal"

site_location = site_name[:3]

# Biosphere
if __name__ == '__main__' :

    # project = "default"
    # # Create a list with the site_name and "Site_{site_name}_number"; numbers should go from 1 to 25
    # for i in range(1,1000) :
    #     project_old = f'Site_{site_name}_{i}'
    #     if project_old in bd.projects :
    #         print(f'Project {project_old} exists')
    #         bd.projects.delete_project(project_old,delete_dir=True)
    #         bd.projects.set_current(project)
    #     else :
    #         print(f'Project {project_old} does not exist')

    project = f'Site_{site_name}_sensitivity_14112024'

    bd.projects.set_current(project)
    print(project)

    #del bd.databases[site_name]
    #del bd.databases[ei_name]


    locations = [("Salton Sea", "Sal"), ("Upper Rhine Valley", "URG")]

    country_location = "US-WECC"

    # print all brightway2 databases
    print(bd.databases)

    eff = 0.5
    Li_conc = 0.018
    abbrev_loc = "Sal"
    op_location = "Salton Sea"

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)


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
        CentrifugeTG(DEFAULT_CONSTANTS,{},),
        washing_TG(),
        dissolution(),
        Liprec_BG(),
        CentrifugeBG(DEFAULT_CONSTANTS,{},),
        washing_BG(),
        CentrifugeWash(DEFAULT_CONSTANTS,{},),
        rotary_dryer()
        ]

    # 1. Define your initial parameters
    prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc], constants=DEFAULT_CONSTANTS)

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}.txt"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename, DEFAULT_CONSTANTS, params={})

    # 3. Run the processes
    dataframes_dict = manager.run(filename)

    max_eff = 0.5
    min_eff = 0.5
    eff_steps = 0.2
    Li_conc_steps = 0.02
    Li_conc_max = 0.03
    Li_conc_min = 0.01

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                   min_eff, eff_steps, Li_conc_steps, Li_conc_max, Li_conc_min, DEFAULT_CONSTANTS, params=None)

    print(results)


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
        CentrifugeTG(DEFAULT_CONSTANTS,SENSITIVITY_RANGES,),
        washing_TG(),
        dissolution(),
        Liprec_BG(),
        CentrifugeBG(DEFAULT_CONSTANTS,SENSITIVITY_RANGES,),
        washing_BG(),
        CentrifugeWash(DEFAULT_CONSTANTS,SENSITIVITY_RANGES,),
        rotary_dryer()
        ]

    # 4. Run the sensitivity analysis
    manager = ProcessManager(initial_data[abbrev_loc],m_pumpbr,prod,process_sequence,filename,
                             constants=DEFAULT_CONSTANTS,
                             params=SENSITIVITY_RANGES)

    sensitivity_results = manager.run_sensitivity_analysis(filename,op_location,abbrev_loc,Li_conc,eff)

    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                             eff, Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map)


    import_aware(ei_reg, bio, site_name, site_db)

    #from src.BW2_calculations.lci_method_pm import import_PM
    #import_PM(ei_reg, bio,site_name, site_db)


    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    #method_PM = [m for m in bd.methods if "PM regionalized" in str(m)][0]
    #print(method_PM)

    method_list = [method_cc,  method_water]



    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]

    sensitivity_impacts = calculate_impacts_for_sensitivity_analysis(activity,method_list,sensitivity_results,site_name,
                                                                     ei_name,abbrev_loc)
    #
    #
    saving_sensitivity_results(sensitivity_impacts,abbrev_loc,
                               save_dir=r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\sensitivity_results')

    # impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
    #                                                    site_name, ei_name,abbrev_loc, eff_range, Li_conc_range
    #                                                    )
    # print(impacts)
    #
    # # saving results
    # from src.BW2_calculations.impact_assessment import saving_LCA_results
    #
    # saving_LCA_results(impacts, abbrev_loc)
    #
    # from src.Postprocessing_results.visualization_functions import Visualization
    # # Plot the results
    # Visualization.plot_impact_categories(impacts, abbrev_loc)




