import os
import numpy as np
import pandas as pd
import datetime
from src.LifeCycleInventoryModel_Li.import_site_parameters import standard_values
from src.BW2_calculations.lci_site_db import chemical_map
import ast
import plotly.express as px
import plotly.graph_objects as go


def get_category_mapping(df):
    # Check if 'df_Li_adsorption' is present in the DataFrame
    is_li_adsorption_present = 'df_Li_adsorption' in df['Activity'].values

    #Mapping of process names to categories
    category_mapping = {
        'df_ion_exchange_H': 'purification',
        'df_ion_exchange_L': 'purification',
        'df_ion_exchange_H_2': 'purification',
        'df_rotary_dryer': 'Li2CO3 prec.',
        'df_centrifuge_wash' : 'Li2CO3 prec.',
        'df_washing_BG' : 'Li2CO3 prec.',
        'df_centrifuge_BG' : 'Li2CO3 prec.',
        'df_Liprec_BG' : 'Li2CO3 prec.',
        'df_washing_TG' : 'Li2CO3 prec.',
        'df_centrifuge_TG' : 'Li2CO3 prec.',
        'df_Liprec_TG' : 'Li2CO3 prec.',
        'df_dissolution': 'Li2CO3 prec.',
        'df_centrifuge_purification_quicklime' : 'purification',
        'df_B_removal_orgsolvent': 'purification',
        'df_SiFe_removal_limestone': 'pre-treatment',
        'df_MnZn_removal_lime': 'pre-treatment',
        'df_acidification': 'pre-treatment',
        'df_Mg_removal_quicklime': 'purification',
        'df_Mg_removal_sodaash': 'pre-treatment' if is_li_adsorption_present else 'purification',
        'df_sulfate_removal_calciumchloride': 'purification',
        'df_centrifuge_purification_sodaash' : 'purification',
        'df_transport': 'evaporation ponds',
        'df_evaporation_ponds': 'evaporation ponds',
        'df_DLE_evaporation_ponds': 'purification',
        'df_Li_adsorption': 'DLE',
        'df_reverse_osmosis': 'volume reduction',
        'df_triple_evaporator': 'volume reduction',
        'df_nanofiltration': 'volume reduction',
        'df_centrifuge_purification_general_1': 'purification',
        'df_centrifuge_purification_general': 'purification',
        'df_centrifuge_purification_general_2': 'purification',
        'df_centrifuge_general_1' : 'purification',
        'df_centrifuge_general_2': 'purification',
        'df_CaMg_removal_sodiumhydrox': 'purification',
        'df_grinding': 'purification',
        'df_electrodialysis': 'volume reduction',
        'df_washing_general': 'purification'

        }

    return category_mapping

category_mapping_more_detailed = {
    'df_ion_exchange_H': 'df_ion_exchange_H',
    'df_ion_exchange_L': 'df_ion_exchange_H',
    'df_ion_exchange_H_2': 'df_ion_exchange_H',
    'df_rotary_dryer': 'df_Liprec_BG',
    'df_centrifuge_wash' : 'df_Liprec_BG',
    'df_washing_BG' : 'df_Liprec_BG',
    'df_centrifuge_BG' : 'df_Liprec_BG',
    'df_Liprec_BG' : 'df_Liprec_BG',
    'df_washing_TG' : 'df_Liprec_BG',
    'df_centrifuge_TG' : 'df_Liprec_BG',
    'df_Liprec_TG' : 'df_Liprec_BG',
    'df_dissolution': 'df_Liprec_BG',
    'df_centrifuge_purification_quicklime' : 'df_Mg_removal_quicklime',
    'df_Mg_removal_quicklime': 'df_Mg_removal_quicklime',
    'df_Mg_removal_sodaash': 'df_Mg_removal_sodaash',
    'df_centrifuge_purification_sodaash' : 'df_Mg_removal_sodaash',
    'df_transport': 'df_evaporation_ponds',
    'df_evaporation_ponds': 'df_evaporation_ponds',
    'df_DLE_evaporation_ponds': 'df_Li_adsorption',
    'df_Li_adsorption': 'df_Li_adsorption',
    'df_centrifuge_purification_general': 'purification',
    'df_centrifuge_purification_general_2': 'purification'
    }


def read_csv_results(file_path) :
    """
    Reads the CSV file at the given file path and returns a pandas DataFrame.

    :param file_path: The path to the CSV file.
    :return: A pandas DataFrame containing the data from the CSV file.
    """
    try :
        df = pd.read_csv(file_path)
        print("CSV file successfully read.")
        return df
    except FileNotFoundError :
        print("File not found. Please check the file path.")


def preparing_data_for_LCA_results_comparison(file_path, directory_path) :

    excel_data = pd.read_excel(file_path)

    # Transpose the data for easier processing

    transposed_data = excel_data.transpose()

    # Set the first row as the header

    transposed_data.columns = transposed_data.iloc[ 0 ]

    # Drop the first row since it's now the header

    transposed_data = transposed_data.drop(transposed_data.index[ 0 ])

    # Dictionary to group activity status

    activity_status_order = {
        # Early stage
        'Grassroots' : '3 - Exploration - Early stage',
        'Exploration' : '3 - Exploration - Early stage',
        'Target Outline' : '3 - Exploration - Early stage',
        'Commissioning' : '3 - Exploration - Early stage',
        'Prefeas/Scoping' : '3 - Exploration - Early stage',
        'Advanced exploration' : '3 - Exploration - Early stage',
        'Feasibility Started' : '3 - Exploration - Early stage',
        # Late stage
        'Reserves Development' : '2 - Exploration - Late stage',
        'Feasibility' : '2 - Exploration - Late stage',
        'Feasibility complete' : '2 - Exploration - Late stage',
        'Construction started' : '2 - Exploration - Late stage',
        'Construction planned' : '2 - Exploration - Late stage',
        'Preproduction' : '2 - Exploration - Late stage',
        # Mine stage
        #'Preproduction' : '1 - Mine stage',
        'Production' : '1 - Mine stage',
        'Operating' : '1 - Mine stage',
        'Satellite' : '1 - Mine stage',
        'Expansion' : '1 - Mine stage',
        'Limited production' : '1 - Mine stage',
        'Residual production' : '1 - Mine stage'
        }


    sites_info = {}

    for site, row in transposed_data.iterrows() :
        activity_status = row.get("activity_status",None)

        production_value = row.get("production",standard_values.get("production"))
        if pd.isna(production_value) :  # Check if the value is nan
            production_value = standard_values.get("production","Unknown")  # Replace with the default if it's nan

        site_info = {
            "abbreviation" : row[ "abbreviation" ],
            "country_location" : row[ "country_location" ],
            "ini_Li" : row.get("ini_Li", None),
            "Li_efficiency" : row.get("Li_efficiency", None),
            "sum_impurities": row.get("sum_impurities", None),
            "deposit_type" : row.get("deposit_type", None),
            "technology_group": row.get("technology_group", None),
            "activity_status": row.get("activity_status", None),
            "activity_status_order" : activity_status_order.get(activity_status,'4 - Other'),
            "production" : production_value,
            }

        # Add to the main dictionary

        sites_info[ site ] = site_info


    # Dictionary to store the matched results for plotting
    matched_results = {}

    # Process each CSV file in the directory
    for file in os.listdir(directory_path) :
        if file.endswith('.csv') :
            # Extract site abbreviation from the file name
            site_abbreviation = file.split('_')[ 0 ]

            if site_abbreviation == "renewables":
                site_abbreviation = file.split('_')[ 1 ]

            # Find the corresponding site info
            for site, info in sites_info.items() :
                if info[ "abbreviation" ] == site_abbreviation :
                    # Read CSV file
                    csv_data = pd.read_csv(os.path.join(directory_path, file))
                    # Check for matching ini_Li and Li_efficiency
                    for _, row in csv_data.iterrows() :
                        print(row[ 'Li-conc' ], info[ 'ini_Li' ], row[ 'eff' ], info[ 'Li_efficiency' ])

                        if (round(row[ 'Li-conc' ], 3) == round(info[ 'ini_Li' ], 3)
                                and round(row[ 'eff' ],2) == round(info[ 'Li_efficiency' ],2)) :
                            # Store IPCC and AWARE values for the site
                            matched_results[ site ] = {'IPCC' : row[ 'IPCC' ], 'AWARE' : row[ 'AWARE' ]}
                            break  # Found the matching row, no need to check further rows

    return matched_results, sites_info


def simplify_process_name(name) :
    # This function simplifies the process name by removing 'df_' and additional details.
    if name.startswith("'df_") :
        # Remove 'df_' prefix and extra details
        simple_name = name[4 :].split("'")[0].strip()
        return simple_name.replace('_',' ').title()  # Replace underscores with spaces and title-case it
    return name


def categorize_activities(row, chemical_map):
    activity = row['Activity']

    # Categorization logic
    if any(activity.startswith(f"'{chem['activity_name']}'") for chem in chemical_map.values()) :
        return 'chemicals'
    elif 'df_' in activity :
        return 'process'
    elif "'market for natural gas, high pressure' (cubic meter, RoW, None)" in activity :
        return 'heat'
    elif 'electricity, high voltage' in activity :
        return 'electricity'
    else :
        return 'rest'


# Function to categorize details
def categorize_details(details_list, chemical_map, abbrev_loc):
    # Initialize a dictionary to hold categorized details and their summed scores
    categorized = {
        'Heat': [],
        'Electricity': [],
        'Chemicals': [],
        'Water': [],
        'Liquid waste': [],
        'Spent solvent': [],
        'Rest': []
    }

    # Initialize a dictionary to hold the sum of scores for each category
    category_scores = {
        'Heat': 0,
        'Electricity': 0,
        'Chemicals': 0,
        'Water': 0,
        'Liquid waste': 0,
        'Spent solvent': 0,
        'Rest': 0
    }

    # Check each detail and categorize it, summing the scores as well
    for detail in details_list:
        activity, score = detail

        # Check for heat-related activities
        if 'natural gas' in activity.lower():
            categorized['Heat'].append(detail)
            category_scores['Heat'] += score
        # Check for electricity-related activities
        elif 'electricity' in activity.lower():
            categorized['Electricity'].append(detail)
            category_scores['Electricity'] += score
        # Check for chemical-related activities
        elif any(chemical_map[chem]['activity_name'] in activity for chem in chemical_map):
            categorized['Chemicals'].append(detail)
            category_scores['Chemicals'] += score
        elif f'Water_{abbrev_loc}' in activity:
            categorized['Water'].append(detail)
            category_scores['Water'] += score
        elif f'waste_liquid_{abbrev_loc}' in activity:
            categorized['Liquid waste'].append(detail)
            category_scores['Liquid waste'] += score
        elif 'treatment of spent solvent mixture, hazardous waste incineration' in activity:
            categorized['Spent solvent'].append(detail)
            category_scores['Spent solvent'] += score
        # Everything else is classified as 'Rest'
        else:
            categorized['Rest'].append(detail)
            category_scores['Rest'] += score

    return categorized, category_scores


def merge_details(details_list):
    # Create a dictionary to hold the sum of scores for each activity
    details_dict = {}

    for detail in details_list:
        # Unpack the tuple
        activity_name, score = detail

        # If the activity is already in the dictionary, add the score; otherwise, add the activity to the dictionary
        if activity_name in details_dict:
            details_dict[activity_name] += score
        else:
            details_dict[activity_name] = score

    # Convert the dictionary back to the list of tuples format
    merged_details = [(activity, score) for activity, score in details_dict.items()]

    return merged_details



def prepare_data_for_waterfall_diagram(file_path, abbrev_loc):
    df = pd.read_csv(file_path)

    # Get the dynamic category mapping based on the DataFrame
    category_mapping = get_category_mapping(df)

    # Label 'df_' activities as 'process' and others as 'Supplychain'
    df['Location_within_supplychain'] = df['Activity'].apply(lambda x : 'process' if 'df_' in x else 'Supplychain')

    # Initialize an empty set to keep track of indices to delete
    rows_to_delete = set()

    # Iterate over the DataFrame to find 'process' rows
    for i in range(len(df)) :
        current_row = df.iloc[i]

        if 'process' in current_row['Location_within_supplychain'] :
            process_level = current_row['Level']
            last_kept_supplychain_level = None

            # Find and mark 'Supplychain' rows that are level + 1
            for j in range(i + 1,len(df)) :
                next_row = df.iloc[j]

                # Keep the 'Supplychain' row if it's level + 1 relative to the 'process'
                if 'Supplychain' in next_row['Location_within_supplychain'] and next_row[
                    'Level'] == process_level + 1 and last_kept_supplychain_level is None :
                    last_kept_supplychain_level = next_row['Level']

                # Delete subsequent 'Supplychain' rows that are level + 1 compared to the last kept 'Supplychain' row
                elif last_kept_supplychain_level is not None and 'Supplychain' in next_row[
                    'Location_within_supplychain'] and next_row['Level'] > last_kept_supplychain_level :
                    rows_to_delete.add(j)

    # Drop the rows marked for deletion
    df = df.drop(list(rows_to_delete)).reset_index(drop=True)

    process_data = []
    current_process = None
    current_process_level = None
    current_process_score = 0

    # Iterate through each row in the dataframe
    for i,row in df.iterrows() :
        if 'process' in row['Location_within_supplychain'] :
            current_process = row['Activity']
            current_process_level = row['Level']
            current_process_score = row['Score']

            # Find all 'Supplychain' activities at the required level
            supplychain_scores = [(item['Activity'],item['Score']) for index,item in df.iterrows()
                                  if 'Supplychain' in item['Location_within_supplychain'] and item[
                                      'Level'] == current_process_level + 1]

            # Find the score of the next process at level + 1, if it exists
            next_process_score = next((item['Score'] for index,item in df.iterrows()
                                       if 'process' in item['Location_within_supplychain'] and item[
                                           'Level'] == current_process_level + 1),0)

            # Calculate 'rest' by subtracting the sum of the supply chain scores and the next process score from the current process score
            sum_supplychain_scores = sum(score for _,score in supplychain_scores)
            rest = current_process_score - sum_supplychain_scores - next_process_score

            # Append 'rest' to details if not zero
            details = supplychain_scores[:]
            if rest > 0 :
                details.append(('Rest',rest))

            # Append the data for this process
            process_data.append({
                'Activity' : current_process,
                'Score' : current_process_score,
                'Details' : details
                })

    new_process_data = []
    for item in process_data :
        # Check if any key in the category_mapping is a substring of the 'Activity'
        mapped_activity = next((value for key,value in category_mapping.items() if key in item['Activity']),
                               item['Activity'])

        # Now find the existing entry, if any, that matches the mapped_activity
        existing = next((x for x in new_process_data if x['Activity'] == mapped_activity),None)

        if existing :
            # If the activity exists, we merge the details and update the score if it's higher
            existing['Details'] += item['Details']
            existing['Score'] = max(existing['Score'],item['Score'])
        else :
            # If the activity does not exist, we add it to the new list
            item['Activity'] = mapped_activity
            new_process_data.append(item)

    # After merging, we need to ensure that details are unique and merged properly
    for item in new_process_data :
        item['Details'] = merge_details(item['Details'])

    # Categorize details and calculate category scores for the new grouped data
    for item in new_process_data :
        categorized_details,category_scores = categorize_details(item['Details'],chemical_map, abbrev_loc)
        item['Categorized_Details'] = categorized_details
        item['Category_Scores'] = category_scores


    for data in new_process_data :
        if 'Details' in data :
            categorized_details,category_scores = categorize_details(data['Details'],chemical_map, abbrev_loc)
            data['Categorized_Details'] = categorized_details
            data['Category_Scores'] = category_scores  # Store the summed scores for each category


    # Convert to DataFrame
    grouped_process_df = pd.DataFrame(new_process_data)


    return grouped_process_df


def verify_total_category_sums(df):
    # Use the first row for the total score
    total_score_row = df.iloc[0]
    total_score = total_score_row['Score']

    # Initialize the sums for each category
    total_heat = 0
    total_electricity = 0
    total_chemicals = 0
    total_water = 0
    total_waste = 0
    total_solvent = 0
    total_rest = 0

    # Sum the scores for each category
    for index, row in df.iterrows():
        category_scores = row['Category_Scores']
        total_heat += category_scores.get('Heat', 0)
        total_electricity += category_scores.get('Electricity', 0)
        total_chemicals += category_scores.get('Chemicals', 0)
        total_water += category_scores.get('Water', 0)
        total_waste += category_scores.get('Liquid waste', 0)
        total_solvent += category_scores.get('Spent solvent', 0)
        total_rest += category_scores.get('Rest', 0)

    # Calculate the total sum of all categories
    sum_of_all_categories = total_heat + total_electricity + total_chemicals + total_water + total_waste + total_solvent + total_rest

    # Verify if the total sum of all categories matches the total score of the first row
    is_match = abs(total_score - sum_of_all_categories) < 1e-2  # Using a tolerance for floating point comparison

    # Return the results
    return {
        'Total_Score': total_score,
        'Sum_of_All_Categories': sum_of_all_categories,
        'Is_Match': is_match,
        'Total_Heat': total_heat,
        'Total_Electricity': total_electricity,
        'Total_Chemicals': total_chemicals,
        'Total_Water': total_water,
        'Total_Waste': total_waste,
        'Total_Spent solvent': total_solvent,
        'Total_Rest': total_rest
    }


def find_latest_matching_file(directory, li_conc, eff, impact_type):
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return None

    latest_file = None
    latest_time = None

    for file in os.listdir(directory):
        if 'copy' not in file and all(x in file for x in [str(li_conc), str(eff), impact_type, '.csv']):
            # Extract timestamp from the file name
            try:
                parts = file.split('_')
                # Extract the date and time parts based on the known structure
                date_part = parts[-3]  # Date should be the third-last segment
                time_part = parts[-2]  # Time should be the second-last segment
                timestamp_str = f"{date_part}_{time_part}"
                timestamp = datetime.datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                if latest_time is None or timestamp > latest_time:
                    latest_time = timestamp
                    latest_file = file
            except ValueError as e:
                print(f"Error parsing timestamp from {file}: {e}")

    return os.path.join(directory, latest_file) if latest_file else None

def process_data_based_on_excel(excel_path, base_directory):
    excel_data = pd.read_excel(excel_path)
    # Transpose the data for easier processing

    transposed_data = excel_data.transpose()

    # Set the first row as the header

    transposed_data.columns = transposed_data.iloc[0]

    # Drop the first row since it's now the header

    excel_data = transposed_data.drop(transposed_data.index[0])

    for index, row in excel_data.iterrows():
        abbrev_loc = row['abbreviation']
        li_conc = row['ini_Li']
        eff = row['Li_efficiency']

        target_directory = os.path.join(base_directory, f'results_{abbrev_loc}')

        for impact_type in ['climatechange', 'waterscarcity']:
            latest_file_path = find_latest_matching_file(target_directory, li_conc, eff, impact_type)
            if latest_file_path:
                print(f"Processing file: {latest_file_path}")
                prepare_data_for_waterfall_diagram(latest_file_path)
            else:
                print(f"No matching file found for {abbrev_loc}, {impact_type} with Li_conc: {li_conc} and Eff: {eff}")



def process_battery_scores_without_diagrams(csv_file_path,excel_file_path,output_dir) :
    # Create directory to save tables if it doesn't exist
    if not os.path.exists(output_dir) :
        os.makedirs(output_dir)

    # Load the LCA CSV data
    lca_data = pd.read_csv(csv_file_path)

    # Load the site-specific information from the Excel file
    excel_data = pd.read_excel(excel_file_path)

    # Transpose the data for easier processing
    transposed_data = excel_data.transpose()

    # Set the first row as the header
    transposed_data.columns = transposed_data.iloc[0]

    # Drop the first row since it's now the header
    transposed_data = transposed_data.drop(transposed_data.index[0])

    # Dictionary to group activity status
    activity_status_order = {
        # Early stage
        'Grassroots' : '3 - Exploration - Early stage',
        'Exploration' : '3 - Exploration - Early stage',
        'Target Outline' : '3 - Exploration - Early stage',
        'Commissioning' : '3 - Exploration - Early stage',
        'Prefeas/Scoping' : '3 - Exploration - Early stage',
        'Advanced exploration' : '3 - Exploration - Early stage',
        'Feasibility Started' : '3 - Exploration - Early stage',
        # Late stage
        'Reserves Development' : '2 - Exploration - Late stage',
        'Feasibility' : '2 - Exploration - Late stage',
        'Feasibility complete' : '2 - Exploration - Late stage',
        'Construction started' : '2 - Exploration - Late stage',
        'Construction planned' : '2 - Exploration - Late stage',
        # Mine stage
        'Preproduction' : '2 - Exploration - Late stage',
        'Production' : '1 - Mine stage',
        'Operating' : '1 - Mine stage',
        'Satellite' : '1 - Mine stage',
        'Expansion' : '1 - Mine stage',
        'Limited production' : '1 - Mine stage',
        'Residual production' : '1 - Mine stage'
        }

    # Extract site information from the transposed Excel data
    sites_info = {}
    for site,row in transposed_data.iterrows() :
        activity_status = row.get("activity_status",None)
        production_value = row.get("production",None)

        if pd.isna(production_value) :  # Check if the value is nan
            production_value = "Unknown"  # Replace with the default if it's nan

        site_info = {
            "site_name" : site,
            "abbreviation" : row["abbreviation"],
            "country_location" : row["country_location"],
            "ini_Li" : row.get("ini_Li",None),
            "Li_efficiency" : row.get("Li_efficiency",None),
            "deposit_type" : row.get("deposit_type",None),
            "technology_group" : row.get("technology_group",None),
            "activity_status" : row.get("activity_status",None),
            "activity_status_order" : activity_status_order.get(activity_status,'4 - Other'),
            "production" : production_value,
            }

        # Add to the main dictionary
        sites_info[site] = site_info

    # Convert 'sites_info' to DataFrame for easier manipulation
    sites_df = pd.DataFrame.from_dict(sites_info,orient='index').reset_index(drop=True)

    # Merge LCA data with site-specific information using the abbreviation as the key
    merged_data = pd.merge(lca_data,sites_df,left_on='Site',right_on='abbreviation',how='left')

    # Update the Method column with more descriptive names
    merged_data['Method'] = merged_data['Method'].replace({
                                                              "('AWARE regionalized', 'Annual', 'All')" : 'Water Scarcity Impacts',
                                                              "('IPCC 2021', 'climate change', 'global warming potential (GWP100)')" : 'Climate Change Impacts'})

    # Create a new table with the merged information
    new_table = merged_data[
        ['Method','site_name','Impact Score','country_location','activity_status_order','technology_group']]

    # Round Impact Score to 1 digit after the comma
    new_table = new_table.copy()
    new_table['Impact Score'] = new_table['Impact Score'].round(1)

    # Split the table into separate tables for each impact category and save them
    impact_categories = new_table['Method'].unique()
    tables = {}
    for category in impact_categories :
        category_table = new_table[new_table['Method'] == category]
        tables[category] = category_table
        # Save each table to a CSV file
        battery_type = os.path.basename(csv_file_path).split('_')[0]  # Extract battery type from file name
        category_name = category.replace(' ','_').lower()
        file_name = os.path.join(output_dir,f"{battery_type}_impact_{category_name}.csv")
        category_table.to_csv(file_name,index=False)

        # Create summary tables grouped by activity status and technology group
        activity_status_summary = category_table.groupby('activity_status_order')['Impact Score'].agg(
            ['min','max',lambda x : round(x.mean(),1)]).reset_index()
        tech_group_summary = category_table.groupby('technology_group')['Impact Score'].agg(
            ['min','max',lambda x : round(x.mean(),1)]).reset_index()

        # Save the summary tables to CSV files
        activity_status_file = os.path.join(output_dir,
                                            f"{battery_type}_impact_{category_name}_activity_status_summary.csv")
        tech_group_file = os.path.join(output_dir,f"{battery_type}_impact_{category_name}_technology_group_summary.csv")
        activity_status_summary.to_csv(activity_status_file,index=False)
        tech_group_summary.to_csv(tech_group_file,index=False)


def process_battery_scores(csv_file_path,excel_file_path,output_dir) :
    # Create directory to save tables if it doesn't exist
    if not os.path.exists(output_dir) :
        os.makedirs(output_dir)

    # Load the LCA CSV data
    lca_data = pd.read_csv(csv_file_path)

    # Load the site-specific information from the Excel file
    excel_data = pd.read_excel(excel_file_path)

    # Transpose the data for easier processing
    transposed_data = excel_data.transpose()

    # Set the first row as the header
    transposed_data.columns = transposed_data.iloc[0]

    # Drop the first row since it's now the header
    transposed_data = transposed_data.drop(transposed_data.index[0])

    # Dictionary to group activity status
    activity_status_order = {
        # Early stage
        'Grassroots' : '3 - Exploration - Early stage',
        'Exploration' : '3 - Exploration - Early stage',
        'Target Outline' : '3 - Exploration - Early stage',
        'Commissioning' : '3 - Exploration - Early stage',
        'Prefeas/Scoping' : '3 - Exploration - Early stage',
        'Advanced exploration' : '3 - Exploration - Early stage',
        'Feasibility Started' : '3 - Exploration - Early stage',
        # Late stage
        'Reserves Development' : '2 - Exploration - Late stage',
        'Feasibility' : '2 - Exploration - Late stage',
        'Feasibility complete' : '2 - Exploration - Late stage',
        'Construction started' : '2 - Exploration - Late stage',
        'Construction planned' : '2 - Exploration - Late stage',
        # Mine stage
        'Preproduction' : '2 - Exploration - Late stage',
        'Production' : '1 - Mine stage',
        'Operating' : '1 - Mine stage',
        'Satellite' : '1 - Mine stage',
        'Expansion' : '1 - Mine stage',
        'Limited production' : '1 - Mine stage',
        'Residual production' : '1 - Mine stage'
        }

    # Extract site information from the transposed Excel data
    sites_info = {}
    for site,row in transposed_data.iterrows() :
        activity_status = row.get("activity_status",None)
        production_value = row.get("production",None)

        if pd.isna(production_value) :  # Check if the value is nan
            production_value = "Unknown"  # Replace with the default if it's nan

        site_info = {
            "site_name" : site,
            "abbreviation" : row["abbreviation"],
            "country_location" : row["country_location"],
            "ini_Li" : row.get("ini_Li",None),
            "Li_efficiency" : row.get("Li_efficiency",None),
            "deposit_type" : row.get("deposit_type",None),
            "technology_group" : row.get("technology_group",None),
            "activity_status" : row.get("activity_status",None),
            "activity_status_order" : activity_status_order.get(activity_status,'4 - Other'),
            "production" : production_value,
            }

        # Add to the main dictionary
        sites_info[site] = site_info

    # Convert 'sites_info' to DataFrame for easier manipulation
    sites_df = pd.DataFrame.from_dict(sites_info,orient='index').reset_index(drop=True)

    # Merge LCA data with site-specific information using the abbreviation as the key
    merged_data = pd.merge(lca_data,sites_df,left_on='Site',right_on='abbreviation',how='left')

    # Update the Method column with more descriptive names
    merged_data['Method'] = merged_data['Method'].replace({
                                                              "('AWARE regionalized', 'Annual', 'All')" : 'Water Scarcity Impacts',
                                                              "('IPCC 2021', 'climate change', 'global warming potential (GWP100)')" : 'Climate Change Impacts'})

    # Create a new table with the merged information
    new_table = merged_data[
        ['Method','site_name','Impact Score','country_location','activity_status_order','technology_group']]

    # Round Impact Score to 1 digit after the comma
    new_table = new_table.copy()
    new_table['Impact Score'] = new_table['Impact Score'].round(1)

    # Split the table into separate tables for each impact category and save them
    impact_categories = new_table['Method'].unique()
    tables = {}
    for category in impact_categories :
        category_table = new_table[new_table['Method'] == category]
        tables[category] = category_table
        # Save each table to a CSV file
        battery_type = os.path.basename(csv_file_path).split('_')[0]  # Extract battery type from file name
        category_name = category.replace(' ','_').lower()
        file_name = os.path.join(output_dir,f"{battery_type}_impact_{category_name}.csv")
        category_table.to_csv(file_name,index=False)

        # Create summary tables grouped by activity status and technology group
        activity_status_summary = category_table.groupby('activity_status_order')['Impact Score'].agg(
            min='min',max='max',mean=lambda x : round(x.mean(),1)).reset_index()
        tech_group_summary = category_table.groupby('technology_group')['Impact Score'].agg(
            min='min',max='max',mean=lambda x : round(x.mean(),1)).reset_index()

        # Save the summary tables to CSV files
        activity_status_file = os.path.join(output_dir,
                                            f"{battery_type}_impact_{category_name}_activity_status_summary.csv")
        tech_group_file = os.path.join(output_dir,f"{battery_type}_impact_{category_name}_technology_group_summary.csv")
        activity_status_summary.to_csv(activity_status_file,index=False)
        tech_group_summary.to_csv(tech_group_file,index=False)

        # Create visualizations using Plotly
        # 1. Impact Score by Site - Bar Chart
        fig = px.bar(category_table,x='site_name',y='Impact Score',title=f'Impact Score by Site for {category}',
                     labels={'site_name' : 'Site Name','Impact Score' : 'Impact Score'},
                     color_discrete_sequence=['#006400'])  # Use earth tone color
        fig.update_layout(xaxis_tickangle=-45,template='plotly_white',title_font=dict(size=16),title_x=0.5)
        fig.write_image(os.path.join(output_dir, f"{battery_type}_impact_{category_name}_by_site.png"))
        fig.write_image(os.path.join(output_dir, f"{battery_type}_impact_{category_name}_by_site.svg"))


        # 2. Impact Score Summary by Activity Status - Bar Chart
        fig = px.bar(activity_status_summary,x='activity_status_order',y=['min','max','mean'],
                     title=f'Impact Score Summary by Activity Status for {category}',
                     labels={'activity_status_order' : 'Activity Status','value' : 'Impact Score'},
                     barmode='group',
                     color_discrete_sequence=['#FF6347','#4B0000','#800000'])  # Use earth tone color palette
        fig.update_layout(xaxis_tickangle=-45,template='plotly_white',title_font=dict(size=16),title_x=0.5)
        fig.write_image(os.path.join(output_dir,f"{battery_type}_impact_{category_name}_activity_status_summary.png"))
        fig.write_image(os.path.join(output_dir,f"{battery_type}_impact_{category_name}_activity_status_summary.svg"))

        # 3. Impact Score Summary by Technology Group - Bar Chart
        fig = px.bar(tech_group_summary,x='technology_group',y=['min','max','mean'],
                     title=f'Impact Score Summary by Technology Group for {category}',
                     labels={'technology_group' : 'Technology Group','value' : 'Impact Score'},
                     barmode='group',
                     color_discrete_sequence=['#87CEFA','#4682B4','#000080'])  # Use earth tone color palette
        fig.update_layout(xaxis_tickangle=-45,template='plotly_white',title_font=dict(size=16),title_x=0.5)
        fig.write_image(os.path.join(output_dir,f"{battery_type}_impact_{category_name}_technology_group_summary.png"))
        fig.write_image(os.path.join(output_dir,f"{battery_type}_impact_{category_name}_technology_group_summary.svg"))


    print(f'Saved tables and visualizations successfully')



def analyze_and_save_technology_group_stats(input_df):
    # Calculate average, min, and max for 'Climate change impacts' and 'Water scarcity impacts' by 'technology_group'
    technology_group_stats = input_df.groupby('technology_group').agg(
        climate_change_avg=('Climate change impacts', 'mean'),
        climate_change_min=('Climate change impacts', 'min'),
        climate_change_max=('Climate change impacts', 'max'),
        water_scarcity_avg=('Water scarcity impacts', 'mean'),
        water_scarcity_min=('Water scarcity impacts', 'min'),
        water_scarcity_max=('Water scarcity impacts', 'max')
    ).reset_index()

    # Round the numbers to two decimal places
    technology_group_stats = technology_group_stats.round(1)

    return technology_group_stats

def analyze_and_save_activity_status_order_stats(input_df):
    # Calculate average, min, and max for 'Climate change impacts' and 'Water scarcity impacts' by 'activity_status_order'
    activity_status_order_stats = input_df.groupby('activity_status_order').agg(
        climate_change_avg=('Climate change impacts', 'mean'),
        climate_change_min=('Climate change impacts', 'min'),
        climate_change_max=('Climate change impacts', 'max'),
        water_scarcity_avg=('Water scarcity impacts', 'mean'),
        water_scarcity_min=('Water scarcity impacts', 'min'),
        water_scarcity_max=('Water scarcity impacts', 'max')
    ).reset_index()

    # Round the numbers to two decimal places
    activity_status_order_stats = activity_status_order_stats.round(1)

    return activity_status_order_stats

def save_stats_to_excel(tech_stats_df, activity_stats_df, file_path):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        tech_stats_df.to_excel(writer, sheet_name='Technology Group Stats', index=False)
        activity_stats_df.to_excel(writer, sheet_name='Activity Status Order Stats', index=False)

def prepare_data_for_table_IPCC_and_AWARE(data_df, file_contains_renewables):
    # Rename columns based on existing DataFrame structure
    data_df.rename(columns={'IPCC': 'Climate change impacts', 'AWARE': 'Water scarcity impacts'}, inplace=True)

    # Determine the keyword to add to the filename based on whether the file contains "renewables"
    file_suffix = "_renewables" if file_contains_renewables else ""

    # Define updated file paths with the new naming logic
    updated_file_path = rf'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\LCA_results\updated_data_for_Marimekko_{file_suffix}.csv'
    stats_file_path = rf'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\LCA_results\stats_data_{file_suffix}.xlsx'

    # Round the dataframe to one decimal place and save as CSV
    data_df_round = data_df.round(1)
    data_df_round.to_csv(updated_file_path, index=False)

    # Generate statistics
    technology_group_stats = analyze_and_save_technology_group_stats(data_df)
    activity_status_order_stats = analyze_and_save_activity_status_order_stats(data_df)

    # Save statistics to Excel file
    save_stats_to_excel(technology_group_stats, activity_status_order_stats, stats_file_path)

    return print(f'Updated data saved to {updated_file_path} and statistics saved to {stats_file_path}')


def prepare_table_for_energy_provision_comparison(excel_path,results_path,output_file_path) :
    # Load and process the Excel data
    excel_data = pd.read_excel(excel_path)
    transposed_data = excel_data.transpose()
    transposed_data.columns = transposed_data.iloc[0]
    excel_data = transposed_data.drop(transposed_data.index[0])

    # Extract relevant rows in the transposed data
    sites_info = {}

    for site,row in transposed_data.iterrows() :
        activity_status = row.get("activity_status",None)

        # Standard values and activity_status_order should be defined somewhere in your script
        production_value = row.get("production",standard_values.get("production"))
        if pd.isna(production_value) :  # Check if the value is nan
            production_value = standard_values.get("production","Unknown")  # Replace with the default if it's nan

        site_info = {
            "site_name" : site,
            "abbreviation" : row["abbreviation"],
            "country_location" : row["country_location"],
            "ini_Li" : row.get("ini_Li",None),
            "Li_efficiency" : row.get("Li_efficiency",None),
            "deposit_type" : row.get("deposit_type",None),
            "technology_group" : row.get("technology_group",None),
            "activity_status" : row.get("activity_status",None),
            "production" : production_value,
            }

        # Add to the main dictionary
        sites_info[site] = site_info

    # Convert 'sites_info' to DataFrame for easier manipulation
    sites_df = pd.DataFrame.from_dict(sites_info,orient='index').reset_index(drop=True)

    # Extract relevant columns
    site_names = sites_df['site_name']
    abbreviations = sites_df['abbreviation']
    technology_groups = sites_df['technology_group']
    ini_Li = sites_df['ini_Li']
    Li_efficiency = sites_df['Li_efficiency']

    # Initialize an empty DataFrame for the final results
    final_results = pd.DataFrame(
        columns=["Site name","Technology group","Li-conc","eff","Change - IPCC","Change - AWARE"])

    # Iterate through each site abbreviation
    for site_name,abbreviation,technology_group,li_conc,li_eff in zip(site_names,abbreviations,technology_groups,ini_Li,
                                                                      Li_efficiency) :
        if pd.isna(abbreviation) or abbreviation == 'abbreviation' :
            continue

        # Define file paths for original and renewable data dynamically
        original_file_path = os.path.join(results_path,'LCA_results',
                                          f"{abbreviation}_eff_{li_eff}_to_{li_eff}_LiConc_{li_conc}_to_{li_conc}.csv")
        renewable_file_path = os.path.join(results_path,'Renewable_assessment',
                                           f"renewables_{abbreviation}_eff_{li_eff}_to_{li_eff}_LiConc_{li_conc}_to_{li_conc}.csv")

        # Debug: Print the file paths being checked
        print(f"Checking files for site: {site_name}, abbreviation: {abbreviation}")
        print(f"Original file path: {original_file_path}")
        print(f"Renewable file path: {renewable_file_path}")

        # Check if both files exist
        if os.path.exists(original_file_path) and os.path.exists(renewable_file_path) :
            original_data = pd.read_csv(original_file_path)
            renewable_data = pd.read_csv(renewable_file_path)

            # Merge datasets and calculate percentages
            merged_data = pd.merge(original_data,renewable_data,on=['Li-conc','eff'],
                                   suffixes=('_original','_renewable'))
            merged_data['IPCC_percentage'] = -(100 - ((merged_data['IPCC_renewable'] / merged_data['IPCC_original']) * 100))
            merged_data['AWARE_percentage'] = -(100 - ((merged_data['AWARE_renewable'] / merged_data['AWARE_original']) * 100))

            # Add site information to the final results
            for _,row in merged_data.iterrows() :
                final_results = final_results.append({
                    "Site name" : site_name,
                    "Technology group" : technology_group,
                    "Li-conc" : row['Li-conc'],
                    "eff" : row['eff'],
                    "Change - IPCC": f"{round(row['IPCC_percentage'], 1)} %",
                    "Change - AWARE": f"{round(row['AWARE_percentage'], 1)} %"
                    },ignore_index=True)

        else :
            print(f"Files for {site_name} with abbreviation {abbreviation} not found.")

    new_file_name = f"energy_provision_comparison_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    new_output_file_dir = os.path.join(output_file_path,new_file_name)

    final_results.to_csv(new_output_file_dir,index=False)

    print(f'New file saved to {new_output_file_dir}')
    return final_results
