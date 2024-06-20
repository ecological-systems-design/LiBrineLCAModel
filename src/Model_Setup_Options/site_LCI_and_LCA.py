import bw2data as bd
from pathlib import Path
import os
import shutil
import bw2io as bw2io

# Import necessary modules from your script
from src.BW2_calculations.lithium_site_db import copy_database
from src.LifeCycleInventoryModel_Li.import_site_parameters import extract_data, update_config_value
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
from src.BW2_calculations.setting_up_db_env import *
from src.BW2_calculations.lci_method_aware import import_aware
from src.BW2_calculations.impact_assessment import calculate_impacts_for_selected_scenarios, saving_LCA_results, saving_LCA_results_brinechemistry, calculate_impacts_for_brine_chemistry, calculate_battery_impacts, save_battery_results_to_csv, print_recursive_calculation
from src.Postprocessing_results.visualization_functions import Visualization
from src.BW2_calculations.modification_bw2 import change_energy_provision
from src.LifeCycleInventoryModel_Li.operational_and_environmental_constants import DEFAULT_CONSTANTS as constants, SENSITIVITY_RANGES as params


def create_process_instance(process_class, constants, params, custom_name=None):
    try:
        if custom_name:
            return process_class(constants=constants, params=params, custom_name=custom_name)
        else:
            return process_class(constants=constants, params=params)
    except TypeError:
        if custom_name:
            return process_class(custom_name=custom_name)
        else:
            return process_class()


def get_process_sequence(process_names, constants, params):
    sequence = []
    ion_exchange_H_count = 0  # Counter for ion_exchange_H
    ion_exchange_L_count = 0  # Counter for ion_exchange_L
    centrifuge_general_count = 0  # Counter for centrifuge_general

    for proc in process_names:
        if proc == 'ion_exchange_H':
            ion_exchange_H_count += 1
            custom_name = None if ion_exchange_H_count == 1 else f"df_ion_exchange_H_{ion_exchange_H_count}"
            print(f"Instantiating process: ion_exchange_H with custom name {custom_name}")
            sequence.append(process_function_map['ion_exchange_H'](constants, params, custom_name))
        elif proc == 'ion_exchange_L':
            ion_exchange_L_count += 1
            custom_name = None if ion_exchange_L_count == 1 else f"df_ion_exchange_L_{ion_exchange_L_count}"
            print(f"Instantiating process: ion_exchange_L with custom name {custom_name}")
            sequence.append(process_function_map['ion_exchange_L'](constants, params, custom_name))
        elif proc == 'Centrifuge_general':
            centrifuge_general_count += 1
            custom_name = None if centrifuge_general_count == 1 else f"df_centrifuge_general_{centrifuge_general_count}"
            print(f"Instantiating process: Centrifuge_general with custom name {custom_name}")
            sequence.append(process_function_map['Centrifuge_general'](constants, params, custom_name))
        elif proc in process_function_map:
            print(f"Instantiating process: {proc}")
            sequence.append(process_function_map[proc](constants, params))
        else:
            print(f"Process not found in the map: {proc}")

    return sequence


def get_process_sequence_old_old(process_names, constants, params):
    sequence = []
    ion_exchange_H_count = 0  # Counter for ion_exchange_H
    ion_exchange_L_count = 0  # Counter for ion_exchange_L
    centrifuge_general_count = 0  # Counter for centrifuge_general

    for proc in process_names:
        if proc == 'ion_exchange_H':
            ion_exchange_H_count += 1
            custom_name = None if ion_exchange_H_count == 1 else f"df_ion_exchange_H_{ion_exchange_H_count}"
            print(f"Instantiating process: ion_exchange_H with custom name {custom_name}")
            sequence.append(process_function_map['ion_exchange_H'](constants, params, custom_name))
        elif proc == 'ion_exchange_L':
            ion_exchange_L_count += 1
            custom_name = None if ion_exchange_L_count == 1 else f"df_ion_exchange_L_{ion_exchange_L_count}"
            print(f"Instantiating process: ion_exchange_L with custom name {custom_name}")
            sequence.append(process_function_map['ion_exchange_L'](constants, params, custom_name))
        elif proc == 'Centrifuge_general':
            centrifuge_general_count += 1
            custom_name = None if centrifuge_general_count == 1 else f"df_centrifuge_general_{centrifuge_general_count}"
            print(f"Instantiating process: Centrifuge_general with custom name {custom_name}")
            sequence.append(process_function_map['Centrifuge_general'](constants, params, custom_name))
        elif proc in process_function_map:
            print(f"Instantiating process: {proc}")
            sequence.append(process_function_map[proc](constants, params))
        else:
            print(f"Process not found in the map: {proc}")

    return sequence


def get_process_sequence_old(process_names):
    sequence = []
    ion_exchange_H_count = 0  # Counter for ion_exchange_H
    ion_exchange_L_count = 0  # Counter for ion_exchange_L
    centrifuge_general_count = 0 # Counter for centrifuge_general

    for proc in process_names:
        if proc == 'ion_exchange_H':
            ion_exchange_H_count += 1
            custom_name = None if ion_exchange_H_count == 1 else f"df_ion_exchange_H_{ion_exchange_H_count}"
            print(f"Instantiating process: ion_exchange_H with custom name {custom_name}")
            sequence.append(ion_exchange_H(custom_name=custom_name))
        elif proc == 'ion_exchange_L':
            ion_exchange_L_count += 1
            custom_name = None if ion_exchange_L_count == 1 else f"df_ion_exchange_L_{ion_exchange_L_count}"
            print(f"Instantiating process: ion_exchange_L with custom name {custom_name}")
            sequence.append(ion_exchange_L(custom_name=custom_name))
        elif proc == 'Centrifuge_general':
            centrifuge_general_count += 1
            custom_name = None if centrifuge_general_count == 1 else f"df_centrifuge_general_{centrifuge_general_count}"
            print(f"Instantiating process: Centrifuge_general with custom name {custom_name}")
            sequence.append(Centrifuge_general(custom_name=custom_name))

        elif proc in process_function_map:
            print(f"Instantiating process: {proc}")
            sequence.append(process_function_map[proc]())
        else:
            print(f"Process not found in the map: {proc}")

    return sequence




def extract_sites_and_abbreviations(excel_file_path):
    # Load the Excel file
    excel_data = pd.read_excel(excel_file_path, sheet_name="Sheet1", index_col=0)

    # Transpose the data for easier row (site) access
    transposed_data = excel_data.T

    # Extract and return the list of site names
    sites_list = transposed_data.index.tolist()

    # Extract abbreviations (assuming they are in the second row)
    abbreviations = transposed_data['abbreviation'].tolist()

    # Create a dictionary mapping site names to their abbreviations
    site_abbreviations = dict(zip(sites_list, abbreviations))

    return site_abbreviations

def create_dbs_without_water_regionalization(project, site_name, site_location, country_location, process_sequence, abbrev_loc):

    # Set up project and databases
    bd.projects.set_current(project)

    # Initialize the processing sequence
    initial_data = extract_data(site_name, abbrev_loc)
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


    return print(f'Created databases for {site_name} without water regionalization')

def run_operation_analysis_with_literature_data(project, site_name, site_location, country_location, process_sequence, abbrev_loc):


    # Set up project and databases

    bd.projects.set_current(project)

    # Initialize the processing sequence
    initial_data = extract_data(site_name, abbrev_loc)
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

    copy_site_db = copy_database(site_name, f'copy_{site_name}')

    change_energy_provision(ei_name, f'copy_{site_name}', country_location, abbrev_loc)

    print(f'Copied database for {site_name}')

    # Importing impact assessment methods
    import_aware(ei_reg, bio, site_name, site_db, copy_site_db)

    # Select impact assessment methods
    method_cc = [m for m in bd.methods if
                 'IPCC 2021' in str(m) and 'climate change' in str(m) and 'global warming potential' in str(m)][-20]
    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]
    method_list = [method_cc, method_water]

    # Calculate and plot impacts
    activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    impacts = calculate_impacts_for_selected_scenarios(activity, method_list, results, site_name, ei_name, abbrev_loc,
                                                       None, None, literature_eff, literature_Li_conc, None)
    # Saving results
    saving_LCA_results(impacts,abbrev_loc)

    #Assessment of renewable energies as an energy supply for brines
    new_activity = [act for act in copy_site_db if "df_rotary_dryer" in act['name']][0]
    new_impacts = calculate_impacts_for_selected_scenarios(new_activity, method_list, results, f'copy_{site_name}', ei_name, abbrev_loc,
                                                       None, None, literature_eff, literature_Li_conc, renewables=True)
    # Saving results
    saving_LCA_results(new_impacts,abbrev_loc, renewable=True)

    #Battery assessment
    act_nmc_battery = [act for act in ei_reg if "battery production, Li-ion, NMC811, rechargeable, prismatic" in act['name']
                       and "CN" in act['location']][0]
    act_lfp_battery = [act for act in ei_reg if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                       and "CN" in act['location']][0]
    act_battery_list = [act_nmc_battery, act_lfp_battery]
    battery_directory = f"results/rawdata/battery_assessment"

    for battery in act_battery_list:
        battery_impacts = calculate_battery_impacts(battery, method_list, site_db, ei_reg, country_location)
        save_battery_results_to_csv(battery_directory, battery_impacts, abbrev_loc, battery)

        battery_files = {
            "NMC811" : "NMC811_recursive_calculation",
            "LFP" : "LFP_recursive_calculation"
            }

        # Extract battery type from the activity name
        battery_type = None
        for key in battery_files.keys() :
            if key in battery['name'] :
                battery_type = key
                break

        print(f'Battery type: {battery_type}')

        # Check if the battery type was found and get the filename
        if battery_type :
            filename = battery_files[battery_type]
            print(battery)
            print_recursive_calculation(battery,method_cc,abbrev_loc,filename,max_level=30,cutoff=0.01)
            print(f'Using {filename} as filename')
        else :
            print('Battery type not recognized')
            return  # Exit the function early if battery type is not recognized




    return impacts

def run_operation_analysis_with_brine_chemistry(project, site_name, site_location, country_location, process_sequence, abbrev_loc, site_data):

    # Set up project and databases

    bd.projects.set_current(project)

    # Initialize the processing sequence
    initial_data = site_data
    print(site_data)
    eff = initial_data[abbrev_loc]['Li_efficiency']
    Li_conc = initial_data[abbrev_loc]['vec_ini'][0]
    print(Li_conc)

    # Define initial parameters and setup site
    prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc])
    filename = f"{abbrev_loc}_eff{eff}_Li{Li_conc}"

    # Initialize the ProcessManager with the given process sequence
    manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

    # Run the processes and simulations
    dataframes_dict = manager.run(filename)
    print(f'Before calculation - initial data: {initial_data}')
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
    impacts = calculate_impacts_for_brine_chemistry(activity, method_list, results, site_name, ei_name, abbrev_loc,
                                                       None, None, literature_eff, literature_Li_conc)
    #Visualization.plot_impact_categories(impacts, abbrev_loc)

    # Saving results
    saving_LCA_results_brinechemistry(impacts, abbrev_loc)

    return impacts

def run_analysis_for_all_sites(excel_file_path, directory_path):
    # Extract site names and their abbreviations
    site_abbreviations = extract_sites_and_abbreviations(excel_file_path)

    # Iterate over each site and its abbreviation
    for site_name, abbreviation in site_abbreviations.items():
        site_data = extract_data(site_name, abbreviation)
        target_ini_Li = site_data[abbreviation]['ini_Li']
        target_eff = site_data[abbreviation]['Li_efficiency']
        project_old = f'Site_{site_name}_literature_values_7'
        project = f'Site_{site_name}_literature_values_8'
        print(f"Currently assessing: {project}")
        old_project_exists = project_old in bd.projects
        if old_project_exists:
            bd.projects.delete_project(project_old, delete_dir=True)
            bd.projects.set_current("Default")

        # Initialize flags to check the existence of project and results
        project_exists = project in bd.projects
        results_exist = False
        # Check for existing result files for the site

        if project_exists :
            # Iterate through each file in the directory
            for file in os.listdir(directory_path) :
                # Check if the file is a CSV file that starts with the given abbreviation
                if file.startswith(abbreviation) and file.endswith('.csv') :
                    csv_data = pd.read_csv(os.path.join(directory_path,file))
                    # Check each row in the CSV file
                    for _,row in csv_data.iterrows() :
                        # Round both values to 5 decimal places before comparing
                        if round(row['Li-conc'],5) == round(target_ini_Li,5) and round(row['eff'],5) == round(
                                target_eff,5) :
                            print(f"Results already exist for site {site_name} with abbreviation {abbreviation}.")
                            results_exist = True
                            break  # Exit the loop as we found the results

                    if results_exist :
                        break  # Exit the file loop as we found the results in one of the files

            # Check if results_exist is still False after checking all files
            if not results_exist :
                print(f"No results found for site {site_name} with abbreviation {abbreviation}.")
                bd.projects.set_current("Default")
                # Delete the project as no results are found in any file
                bd.projects.delete_project(project,delete_dir=True)
                bd.projects.set_current(project)


        # Print status
        if project_exists:
            print(f"Project '{project}' already exists. If no results are reported, then it is deleted.")
        if results_exist:
            print(f"Results already exist for site {site_name} with abbreviation {abbreviation}.")

        # Run analysis only if project and results don't exist
        if not results_exist:
            # Extract process sequence and country location
            process_sequence = get_process_sequence(site_data[abbreviation]['process_sequence'])
            country_location = site_data[abbreviation]['country_location']
            site_location = site_name
            print(f'Currently assessing: {site_name}')
            # Run operation analysis for the site
            impacts = run_operation_analysis_with_literature_data(project, site_name, site_location, country_location, process_sequence, abbreviation)
            # Handle 'impacts' as needed
        else:
            print(f"Skipping analysis for site {site_name}.")

def run_analysis_for_all_sites_to_extract_dbs(excel_file_path, directory_path):
    # Extract site names and their abbreviations
    site_abbreviations = extract_sites_and_abbreviations(excel_file_path)

    # Iterate over each site and its abbreviation
    for site_name, abbreviation in site_abbreviations.items():
        site_data = extract_data(site_name, abbreviation)
        target_ini_Li = site_data[abbreviation]['ini_Li']
        target_eff = site_data[abbreviation]['Li_efficiency']
        old_project = f'{site_name}_databases_08062024'
        project = f'{site_name}_databases_11062024'
        print(f"Currently assessing: {project}")

        if old_project in bd.projects:
            bd.projects.delete_project(old_project, delete_dir=True)
            bd.projects.set_current("Default")

        # Initialize flags to check the existence of project and results
        project_exists = project in bd.projects

        if not project_exists :
            bd.projects.set_current(project)
            process_sequence = get_process_sequence(site_data[abbreviation]['process_sequence'])
            country_location = site_data[abbreviation]['country_location']
            site_location = site_name
            create_dbs_without_water_regionalization(project, site_name, site_location, country_location, process_sequence, abbreviation)
        else:
            bd.projects.set_current(project)

        dbs_for_export = [site_name]
        for db in dbs_for_export :
            # This will export the LCI database as an Excel file and save it in the BW2 project directory.
            # The exact directory is printed
            export_path = bw2io.export.excel.write_lci_excel(db)
            print(export_path)

            # This will copy the Excel files to the current directory:
            current_path = os.getcwd()
            shutil.copy(export_path,current_path)

        print(f"Project '{project}' already exists. Databases are exported.")






def run_analysis_for_brinechemistry(excel_file_path, directory_path):
    # Extract site names and their abbreviations
    site_abbreviations = extract_sites_and_abbreviations(excel_file_path)
    print(site_abbreviations)

    # Iterate over each site and its abbreviation
    for site_name, abbreviation in site_abbreviations.items():
        print(f'Site_name: {site_name}, abbreviation: {abbreviation}')

        # Get the list of brine chemistry analyses for the site
        brine_chemistry_sets = prepare_brine_analyses(excel_file_path, abbreviation)
        print(brine_chemistry_sets)

        # Check if there are no brine chemistry analyses for the site and skip to the next if so
        if not brine_chemistry_sets :
            print(f"No brine chemistry analyses found for {site_name}. Skipping to next site.")
            continue
        else :

            # Iterate over the values of brine_chemistry_sets, which are the lists of analysis values
            for analysis_id, vec_ini_list in brine_chemistry_sets.items() :

                # Call extract_data for each set of brine chemistry analyses
                site_data = extract_data(site_location=site_name,abbrev_loc=abbreviation,Li_conc=None,
                                         vec_ini=vec_ini_list)
                # Initialize a flag to check the existence of results
                results_exist = False
                target_ini_Li = site_data[abbreviation]['vec_ini'][0]
                target_eff = site_data[abbreviation]['Li_efficiency']

                process_sequence = get_process_sequence(site_data[abbreviation]['process_sequence'], constants, params)
                site_location = site_name
                country_location = site_data[abbreviation]['country_location']
                project = f'Site_{site_location}_brinechemistry_final1'
                project_exist = project in bd.projects

                # Check for existing result files for the site
                if project_exist :
                    for file in os.listdir(directory_path) :
                        if file.startswith(abbreviation) and file.endswith('.csv') :
                            csv_data = pd.read_csv(os.path.join(directory_path,file))
                            for _,row in csv_data.iterrows() :
                                # Round both values to 5 decimal places before comparing
                                if round(row['Li-conc'],5) == round(target_ini_Li,5) and round(row['eff'],5) == round(
                                        target_eff,5) :
                                    print(f"Results already exist for site {site_name} with abbreviation {abbreviation}.")
                                    results_exist = True
                            if results_exist :
                                break

                    if results_exist :
                        # Skip to the next site if results already exist
                        continue
                    else:
                        print(f"No results found for site {site_name} with abbreviation {abbreviation}.")
                        process_sequence = get_process_sequence(site_data[abbreviation]['process_sequence'])
                        # Assigning the site location and country location
                        site_location = site_name
                        country_location = site_data[abbreviation]['country_location']

                        # Run operation analysis for the site with the extracted information
                        impacts = run_operation_analysis_with_brine_chemistry(project,site_name,site_location,
                                                                              country_location,process_sequence,
                                                                              abbreviation,site_data)

                else :
                    #site_data = extract_data(site_name, abbreviation)
                    process_sequence = get_process_sequence(site_data[ abbreviation ][ 'process_sequence' ])
                    # Assigning the site location and country location
                    site_location = site_name
                    country_location = site_data[ abbreviation ][ 'country_location' ]

                    # Run operation analysis for the site with the extracted information
                    impacts = run_operation_analysis_with_brine_chemistry(project, site_name, site_location,
                                                                          country_location, process_sequence, abbreviation, site_data)

