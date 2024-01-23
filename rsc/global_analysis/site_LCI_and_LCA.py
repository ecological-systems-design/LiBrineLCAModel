import bw2data as bd
from pathlib import Path
import os

# Import necessary modules from your script
from rsc.lithium_production.import_site_parameters import extract_data, update_config_value
from rsc.lithium_production.licarbonate_processes import *
from rsc.Brightway2.setting_up_db_env import *
from rsc.Brightway2.lci_method_aware import import_aware
from rsc.Brightway2.impact_assessment import calculate_impacts_for_selected_scenarios, saving_LCA_results
from rsc.Postprocessing_results.visualization_functions import Visualization

def run_operation_analysis_with_literature_data(project, site_name, site_location, country_location, process_sequence):

    # Ensure 'results' directory exists
    if not os.path.exists("results") :
        os.mkdir("results")

    # Set up project and databases

    bd.projects.set_current(project)

    # Initialize the processing sequence
    initial_data, abbrev_loc = extract_data(site_name)
    eff = initial_data[abbrev_loc]['Li_efficiency']
    Li_conc = initial_data[abbrev_loc]['vec_ini'][0]

    # Define initial parameters and setup site
    prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc])
    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}"

    # Initialize the ProcessManager with the given process sequence
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

    # Run the processes and simulations
    dataframes_dict = manager.run(filename)
    results, literature_eff, literature_Li_conc = manager.run_simulation_with_literature_data(site_location, abbrev_loc,
                                                                                              process_sequence,
                                                                                              site_parameters=
                                                                                              initial_data[abbrev_loc])

    # Setting up databases for environmental impact calculation
    biosphere = "biosphere3"
    ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
    ei_name = "ecoinvent 3.9.1 cutoff"
    deposit_type = initial_data[abbrev_loc]['deposit_type']
    ei_reg, site_db, bio = database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location,
                                                eff, Li_conc, site_location, abbrev_loc, dataframes_dict, chemical_map)

    # Importing impact assessment methods
    import_aware(ei_reg, bio, site_name, site_db)

    # Select impact assessment methods
    method_cc = [m for m in bd.methods if
                 'IPCC 2021' in str(m) and 'climate change' in str(m) and 'global warming potential' in str(m)][-20]
    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]
    method_list = [method_cc, method_water]

    # Calculate and plot impacts
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results, site_name, ei_name, abbrev_loc,
                                                       None, None, literature_eff, literature_Li_conc)
    Visualization.plot_impact_categories(impacts, abbrev_loc)

    # Saving results
    saving_LCA_results(impacts, abbrev_loc)

    return impacts

