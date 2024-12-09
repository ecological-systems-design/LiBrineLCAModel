import bw2data as bd
from pathlib import Path
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
import os
from src.LifeCycleInventoryModel_Li.import_site_parameters import extract_data, update_config_value
from src.BW2_calculations.lci_method_aware import import_aware
from src.BW2_calculations.setting_up_db_env import *
from src.BW2_calculations.impact_assessment import saving_LCA_results, print_recursive_calculation

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salar del Hombre Muerto North"
biosphere = f"biosphere3"
deposit_type = "salar"

site_location = "Hom"

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_18'
    bd.projects.set_current(project)
    print(project)

    #del bd.databases[site_name]
    # del bd.databases[ei_name]

    country_location = "AR"

    # print all brightway2 databases
    print(bd.databases)

    eff = 0.45
    Li_conc = 0.15
    abbrev_loc = "Hom"
    op_location = "Salar del Hombre Muerto North"

    # initialize the processing sequence

    initial_data = extract_data(op_location, abbrev_loc, Li_conc)

    process_sequence = [
        evaporation_ponds(),
        transport_brine(),
        B_removal_organicsolvent(),
        Centrifuge_general(DEFAULT_CONSTANTS,{},custom_name=None),
        Mg_removal_sodaash(),
        CentrifugeSoda(DEFAULT_CONSTANTS,{}),
        Mg_removal_quicklime(),
        CentrifugeQuicklime(DEFAULT_CONSTANTS,{}),
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
    print(f'before setting up site: {abbrev_loc}')

    prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc], constants=DEFAULT_CONSTANTS)

    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}"

    print(initial_data[abbrev_loc])

    # 2. Initialize the ProcessManager
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename,DEFAULT_CONSTANTS, params={})

    # 3. Run the processes
    dataframes_dict = manager.run(filename)

    max_eff = 0.46
    min_eff = 0.45
    eff_steps = 0.01
    Li_conc_steps = 0.02
    Li_conc_max = 0.066169154
    Li_conc_min = 0.05

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                                                               min_eff, eff_steps, Li_conc_steps, Li_conc_max,
                                                               Li_conc_min, DEFAULT_CONSTANTS, params={})

    print(results)


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

    from src.BW2_calculations.impact_assessment import calculate_impacts_for_selected_scenarios

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, abbrev_loc, eff_range, Li_conc_range)
    #print(impacts)

    # saving results

    saving_LCA_results(impacts, abbrev_loc)

    # Battery assessment
    act_nmc_battery = \
    [act for act in ei_reg if "battery production, Li-ion, NMC811, rechargeable, prismatic" in act['name']
     and "CN" in act['location']][0]
    act_lfp_battery = \
    [act for act in ei_reg if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
     and "CN" in act['location']][0]
    act_battery_list = [act_nmc_battery,act_lfp_battery]
    directory = f"results/test"

    from src.BW2_calculations.impact_assessment import calculate_battery_impacts, save_battery_results_to_csv

    for battery in act_battery_list :
        battery_impacts = calculate_battery_impacts(battery,method_list,site_db,ei_reg,country_location)
        save_battery_results_to_csv(directory,battery_impacts,abbrev_loc,battery)

        battery_files = {
            "NMC811" : "NMC811_recursive_calculation.csv",
            "LFP" : "LFP_recursive_calculation.csv"
            }

        # Extract battery type from the activity name
        battery_type = None
        for key in battery_files.keys() :
            if key in battery['name'] :
                battery_type = key
                break

        # Check if the battery type was found and get the filename
        if battery_type :
            filename = battery_files[battery_type]
            print_recursive_calculation(battery,method_cc,abbrev_loc,filename,max_level=30,cutoff=0.01)
            print(f'Using {filename} as filename')
        else :
            print('Battery type not recognized')




    # Plot the results
    #Visualization.plot_impact_categories(impacts, abbrev_loc)


