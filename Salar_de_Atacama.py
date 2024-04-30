import os
from pathlib import Path
import pickle
from rsc.Brightway2.impact_assessment import calculate_impacts_for_selected_scenarios
from rsc.lithium_production.licarbonate_processes import *
import bw2data as bd
from rsc.lithium_production.import_site_parameters import extract_data, update_config_value
from rsc.Brightway2.setting_up_db_env import *
from rsc.Brightway2.lci_method_aware import import_aware
from rsc.Brightway2.lci_method_pm import import_PM
from rsc.Brightway2.impact_assessment import saving_LCA_results, print_recursive_calculation, calculate_battery_impacts,save_battery_results_to_csv

if not os.path.exists("results") :
    os.mkdir("results")

# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salar de Atacama"
biosphere = f"biosphere3"
deposit_type = "salar"

site_location = "Ata"

# Biosphere
if __name__ == '__main__' :

    project = f'Site_{site_name}_2'
    bd.projects.set_current(project)
    print(project)


    #del bd.databases[site_name]
    #del bd.databases[ei_name]

    country_location = "CL"

    # print all brightway2 databases
    print(bd.databases)

    eff = 0.45
    Li_conc = 0.15
    abbrev_loc = "Ata"
    op_location = "Salar de Atacama"

    # initialize the processing sequence


    initial_data = extract_data(op_location, abbrev_loc, Li_conc)


    process_sequence = [
        evaporation_ponds(),
        transport_brine(),
        B_removal_organicsolvent(),
        Centrifuge_general(custom_name=None),
        Mg_removal_sodaash(),
        CentrifugeSoda(),
        Mg_removal_quicklime(),
        CentrifugeQuicklime(),
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

    max_eff = 0.45
    min_eff = 0.43
    eff_steps = 0.1
    Li_conc_steps = 0.1
    Li_conc_max = 0.15
    Li_conc_min = 0.1

    results, eff_range, Li_conc_range = manager.run_simulation(op_location, abbrev_loc, process_sequence, max_eff,
                                                               min_eff, eff_steps, Li_conc_steps, Li_conc_max,
                                                               Li_conc_min)

    print(results)



    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                eff, Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map)



    import_aware(ei_reg, bio, site_name, site_db)

    #import_PM(ei_reg, bio, site_name, site_db)

    # print(results)

    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    #method_PM = [m for m in bd.methods if "PM regionalized" in str(m)][0]

    method_list = [method_cc, method_water]

    # Calculate impacts for the activity
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]

    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results,
                                                       site_name, ei_name, abbrev_loc, eff_range, Li_conc_range
                                                       )

    # saving results


    # Get efficiency and Li-conc ranges for filename
    efficiencies = [round(eff, 1) for (eff, _) in impacts.keys()]
    Li_concs = [Li_conc for (_, Li_conc) in impacts.keys()]

    min_eff, max_eff = min(efficiencies), max(efficiencies)
    min_Li_conc, max_Li_conc = min(Li_concs), max(Li_concs)

    filename = f"eff_{min_eff}_to_{max_eff}_LiConc_{min_Li_conc}_to_{max_Li_conc}"

    saving_LCA_results(impacts, abbrev_loc)







