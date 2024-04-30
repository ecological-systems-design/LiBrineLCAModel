import os
import numpy as np
import pandas as pd
import datetime
from rsc.lithium_production.import_site_parameters import standard_values
from rsc.Brightway2.lithium_site_db import chemical_map




category_mapping = {
    'df_centrifuge_wash' : 'df_Liprec_BG',
    'df_washing_BG' : 'df_Liprec_BG',
    'df_centrifuge_BG' : 'df_Liprec_BG',
    'df_Liprec_BG' : 'df_Liprec_BG',
    'df_washing_TG' : 'df_Liprec_TG',
    'df_centrifuge_TG' : 'df_Liprec_TG',
    'df_Liprec_TG' : 'df_Liprec_TG',
    'df_centrifuge_purification_quicklime' : 'df_Mg_removal_quicklime',
    'df_Mg_removal_quicklime': 'df_Mg_removal_quicklime',
    'df_Mg_removal_sodaash': 'df_Mg_removal_sodaash',
    'df_centrifuge_purification_sodaash' : 'df_Mg_removal_sodaash',
    'df_transport': 'df_evaporation_ponds',
    'df_evaporation_ponds': 'df_evaporation_ponds',
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
        # Mine stage
        'Preproduction' : '1 - Mine stage',
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
def categorize_details(details_list,chemical_map) :
    # Initialize a dictionary to hold categorized details and their summed scores
    categorized = {
        'Heat' : [],
        'Electricity' : [],
        'Chemicals' : [],
        'Rest' : []
        }

    # Initialize a dictionary to hold the sum of scores for each category
    category_scores = {
        'Heat' : 0,
        'Electricity' : 0,
        'Chemicals' : 0,
        'Rest' : 0
        }

    # Check each detail and categorize it, summing the scores as well
    for detail in details_list :
        activity,score = detail

        # Check for heat-related activities
        if 'natural gas' in activity.lower() :
            categorized['Heat'].append(detail)
            category_scores['Heat'] += score
        # Check for electricity-related activities
        elif 'electricity' in activity.lower() :
            categorized['Electricity'].append(detail)
            category_scores['Electricity'] += score
        # Check for chemical-related activities
        elif any(chem in activity for chem in chemical_map) :
            categorized['Chemicals'].append(detail)
            category_scores['Chemicals'] += score
        # Everything else is classified as 'Rest'
        else :
            categorized['Rest'].append(detail)
            category_scores['Rest'] += score

    return categorized,category_scores

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



def prepare_data_for_waterfall_diagram(file_path):
    df = pd.read_csv(file_path)

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
        categorized_details,category_scores = categorize_details(item['Details'],chemical_map)
        item['Categorized_Details'] = categorized_details
        item['Category_Scores'] = category_scores


    for data in new_process_data :
        if 'Details' in data :
            categorized_details,category_scores = categorize_details(data['Details'],chemical_map)
            data['Categorized_Details'] = categorized_details
            data['Category_Scores'] = category_scores  # Store the summed scores for each category


    # Convert to DataFrame
    grouped_process_df = pd.DataFrame(new_process_data)
    return grouped_process_df


def find_latest_matching_file(directory, li_conc, eff, impact_type):
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return None

    latest_file = None
    latest_time = None

    for file in os.listdir(directory):
        if all(x in file for x in [str(li_conc), str(eff), impact_type, '.csv']):
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


def process_battery_scores(file_path, directory) :
    # get location-specific data by importing xlsx file
    excel_data = pd.read_excel(file_path)

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
        'Preproduction' : '1 - Mine stage',
        'Production' : '1 - Mine stage',
        'Operating' : '1 - Mine stage',
        'Satellite' : '1 - Mine stage',
        'Expansion' : '1 - Mine stage',
        'Limited production' : '1 - Mine stage',
        'Residual production' : '1 - Mine stage'
        }

    sites_info = {}

    for site,row in transposed_data.iterrows() :
        activity_status = row.get("activity_status",None)

        production_value = row.get("production",standard_values.get("production"))
        if pd.isna(production_value) :  # Check if the value is nan
            production_value = standard_values.get("production","Unknown")  # Replace with the default if it's nan

        site_info = {
            "site_name": site,
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



    # Initialize an empty DataFrame to store the results
    results_df = pd.DataFrame(columns=['Location','NMC811','LFP'])

    # Loop through each file in the directory
    for filename in os.listdir(directory) :
        if 'recursive_calculation' in filename and filename.endswith('.csv') :
            parts = filename.split('_')
            battery_type = 'NMC811' if 'NMC811' in filename else 'LFP'
            location_abbreviation = parts[3]
            print(f'print abbrev from file name: {location_abbreviation}')

            # Check for matching site using abbreviation
            if location_abbreviation in sites_df['abbreviation'].values :
                site_details = sites_df[sites_df['abbreviation'] == location_abbreviation].iloc[0]
                site_name = site_details['site_name']
                country = site_details['country_location']
                activity_status_order = site_details['activity_status_order']
                li_conc = site_details['ini_Li']

                print(f'Processing {site_name} for {battery_type}...')


                # Construct the full path to the file
                file_path = os.path.join(directory,filename)

                # Load the CSV file
                data = pd.read_csv(file_path)

                # Get and round the score from Level 0
                score_level_0 = np.round(data[data['Level'] == 0]['Score'].iloc[0],1)

                # Check if the location is already in the DataFrame
                if site_name in results_df['Location'].values :
                    results_df.loc[results_df['Location'] == site_name,battery_type] = score_level_0
                else :
                    # Initialize scores for both types to zero
                    new_scores = {'NMC811' : 0,'LFP' : 0,battery_type : score_level_0}
                    new_row = pd.DataFrame({
                                               'Location' : [site_name],'Country' : [country],
                                               'Activity Status' : [activity_status_order],
                                                'Li-conc.': [li_conc], **new_scores})
                    results_df = pd.concat([results_df,new_row],ignore_index=True)
            else :
                print(f"No site found for abbreviation: {location_abbreviation}")
                continue  # Skip this file if no matching site is found

    # Sort results based on country and activity
    sorted_results_df = results_df.sort_values(by=['Country','Activity Status', 'Li-conc'],ascending=[True,True,False])

    # Save the updated DataFrame
    time_stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    results_filename = f'battery_scores_{time_stamp}.csv'

    sorted_results_df.to_csv(os.path.join(directory,results_filename),index=False)
    print(f"Saved new file {results_filename} to {directory}")

    return results_df

