import os

import numpy as np
import pandas as pd

from rsc.lithium_production.import_site_parameters import standard_values




category_mapping = {
    'df_centrifuge_wash' : 'df_Liprec_BG',
    'df_washing_BG' : 'df_Liprec_BG',
    'df_centrifuge_BG' : 'df_Liprec_BG',
    'df_Liprec_BG' : 'df_Liprec_BG',
    'df_washing_TG' : 'df_Liprec_TG',
    'df_centrifuge_TG' : 'df_Liprec_TG',
    'df_Liprec_TG' : 'df_Liprec_TG',
    "df_centrifuge_purification_quicklime" : "df_Mg_removal_quicklime",
    "df_centrifuge_purification_sodaash" : "df_Mg_removal_sodaash",
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


def preparing_data_recursivecalculation(file_path, category_mapping) :
    df = read_csv_results(file_path)

    df['Location_within_supplychain'] = df['Activity'].apply(lambda x : x if 'df_' in x else 'Supplychain')

    for i in range(len(df)) :
        if i == len(df) - 1 :
            break

        current_row = df.iloc[i]
        next_row = df.iloc[i + 1]

        if 'df_' in current_row['Location_within_supplychain'] :
            df.at[i, 'Category'] = current_row['Location_within_supplychain']

        elif current_row['Location_within_supplychain'] == 'Supplychain' :
            if current_row['Level'] < next_row['Level'] :
                df.at[i, 'Category'] = current_row['Activity']
                df.at[i + 1, 'Activity'] = current_row['Activity']

            else :
                df.at[i, 'Category'] = current_row['Activity']

    df = df[df['Category'] != df['Category'].shift()]
    df = df.sort_values('Level')

    percent_threshold = 1e-6  # Adjust the percent threshold as needed
    total_threshold = 1e-6  # Adjust the total threshold as needed

    for level in df['Level'] :
        rows = df.loc[df['Level'] == level]
        df_level_rest = df.loc[
            (df['Level'] == level) & (df['Category'].str.contains('df_')) & (df['Activity'] == 'rest')]
        if df_level_rest.empty :
            for _, row in rows.iterrows() :
                if 'df_' in row['Category'] :
                    rest = row['Percent'] - df.loc[df['Level'] == level + 1, 'Percent'].sum()
                    rest_tot = row['Total'] - df.loc[df['Level'] == level + 1, 'Total'].sum()
                    if rest >= percent_threshold :
                        new_data = {
                            'Level' : level,
                            'Percent' : rest,
                            'Total' : rest_tot,
                            'Activity' : "rest",
                            'Location_within_supplychain' : "Supplychain",
                            'Category' : row['Category']
                            }
                        df = df.append(new_data, ignore_index=True)
                        print(f"Rest for level {level}: {rest}")
                    else :
                        if abs(rest) < percent_threshold :
                            rest = 0
                            rest_tot = 0
                            new_data = {
                                'Level' : level,
                                'Percent' : rest,
                                'Total' : rest_tot,
                                'Activity' : "rest",
                                'Location_within_supplychain' : "Supplychain",
                                'Category' : row['Category']
                                }
                            df = df.append(new_data, ignore_index=True)

                        else :
                            pass
        else :
            pass

    df = df.sort_values('Level')

    for index, row in df.iterrows() :
        if "deep well drilling, for deep geothermal power" in row['Activity'] :
            level = row['Level']
            matching_rows = df.loc[(df['Level'] == level) & (df['Activity'].str.startswith('df_')), 'Category']
            if len(matching_rows) > 0 :
                category = matching_rows.values[0]

                df.at[index, 'Category'] = category

        elif 'df_' not in row['Activity'] and row['Activity'] != 'rest' :
            # Get the level and category of the corresponding 'df_' row
            level = row['Level']
            matching_rows = df.loc[(df['Level'] == level) & (df['Activity'].str.startswith('df_')), 'Category']

            if len(matching_rows) > 0 :
                category = matching_rows.values[0]

                # Update the Category value in the original dataframe
                df.at[index, 'Category'] = category

    df['Level'] = df.apply(lambda row : row['Level'] - 1 if not (row['Activity'].startswith('df_') or
                                                                 "rest" in row['Activity']) else row['Level'], axis=1)

    for index, row in df.iterrows() :
        if 'df_' not in row['Activity'] :
            level = row['Level']
            matching_row = df[(df['Activity'].str.contains('df_')) & (df['Level'] == level)]
            if not matching_row.empty :
                df.at[index, 'Category'] = matching_row['Category'].values[0]

    df = df[~df['Activity'].str.contains('df_')]

    df['Level'] = df['Level'].max() - df['Level']

    # Group rows based on the specified conditions
    for category, new_category in category_mapping.items() :
        if category in df['Category'].values and "rest" in df['Activity'].values :
            # Filter rows with the current category
            rows_to_group = df[df['Category'] == category]
            print(rows_to_group)
            rows_to_group['Category'] = new_category
            df.update(rows_to_group)

    df = df.groupby(['Category'], as_index=False).agg(
        {"Level" : np.min, "Percent" : np.sum, "Total" : np.sum,
         "Activity" : pd.Series.mode, "Supplychain" : pd.Series.mode})

    df = df.sort_values('Level')
    df['Level'] = 1

    return df


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
                            print(matched_results)
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


def prepare_data_for_visualization_firstrun(file_path) :
    df = pd.read_csv(file_path)

    # Initialize an empty dictionary to hold the aggregated data
    data_for_visualization = {}

    for index,row in df.iterrows() :
        process_name = simplify_process_name(row['Activity'])

        if process_name not in data_for_visualization :
            data_for_visualization[process_name] = {
                'Score' : 0,
                'Contributing Activities' : [],
                'Contributing Activity Scores' : []
                }

        if row['Activity'].startswith("'df_") :
            # Update the process score
            data_for_visualization[process_name]['Score'] += row['Score']
        else :
            # Find the corresponding process to add this activity
            for process,details in data_for_visualization.items() :
                if process in process_name :
                    details['Contributing Activities'].append(process_name)
                    details['Contributing Activity Scores'].append(row['Score'])
                    break

    return data_for_visualization

def prepare_data_for_visualization(file_path, chemical_map):
    df = pd.read_csv(file_path)

    # Initialize an empty dictionary to hold the aggregated data
    data_for_visualization = {}

    for index, row in df.iterrows():
        process_name = simplify_process_name(row['Activity'])

        if process_name not in data_for_visualization:
            data_for_visualization[process_name] = {
                'Score': row['Score'] if row['Activity'].startswith("'df_") else 0,
                'Categories': {'chemicals': 0, 'heat': 0, 'electricity': 0, 'rest': 0}
            }

        # For contributing activities, categorize and sum the scores
        if not row['Activity'].startswith("'df_"):
            category = categorize_activity(row['Activity'], chemical_map)
            data_for_visualization[process_name]['Categories'][category] += row['Score']

    return data_for_visualization


def prepare_data_for_visualization_try_try(file_path, chemical_map):
    df = pd.read_csv(file_path)

    # Initialize a list to store the processed data
    processed_data = []

    # Set to track which df_ processes have their immediate contributing activity identified
    processed_df_activities = set()

    # Iterate over the DataFrame in reverse level order to capture highest contributing activities first
    for level in sorted(df['Level'].unique(), reverse=True):
        current_level_df = df[df['Level'] == level]

        # Iterate over each activity in the current level
        for idx, row in current_level_df.iterrows():
            activity = row['Activity']
            if activity.startswith("'df_"):
                # Directly include 'df_' processes and mark them as processed
                processed_data.append(row)
                processed_df_activities.add(activity)
            else:
                # Check if this activity is an immediate contributing activity
                if not any(act for act in processed_df_activities if act in activity):
                    processed_data.append(row)
                    # Mark this activity's process as having its immediate contributing activity identified
                    processed_df_activities.update(current_level_df['Activity'])

    # Concatenate the list of processed data into a DataFrame and sort
    processed_df = pd.concat(processed_data, axis=1).transpose()
    processed_df = processed_df.sort_values(by='Level')

    # Categorize activities
    processed_df['Category'] = processed_df.apply(lambda row: categorize_activities(row, chemical_map), axis=1)

    return processed_df


def prepare_data_for_visualization_adjusted1(file_path) :
    df = pd.read_csv(file_path)
    processed_data = []

    # Iterate through each unique level in the dataframe
    for level in sorted(df['Level'].unique()) :
        # Get all activities at the current level
        current_level_activities = df[df['Level'] == level]

        for _,activity_row in current_level_activities.iterrows() :
            # Directly add 'df_' activities
            if activity_row['Activity'].startswith("'df_") :
                processed_data.append(activity_row)
                # Find direct contributors that are not 'df_' activities at the next level
                next_level_activities = df[(df['Level'] == level + 1) & (~df['Activity'].str.startswith("'df_"))]
                for _,next_activity_row in next_level_activities.iterrows() :
                    # Check if there's a deeper activity in the supply chain
                    deeper_activities = df[(df['Level'] > level + 1) & (df['Score'] < next_activity_row['Score']) & (
                        df['Activity'].str.contains(next_activity_row['Activity'].split("'")[1]))]

                    processed_data.append(next_activity_row)

    # Convert the list of rows to a DataFrame
    processed_df = pd.DataFrame(processed_data).drop_duplicates().sort_values(by='Level')

    return processed_df

def prepare_data_for_visualization_adjusted2(file_path) :
    df = pd.read_csv(file_path)

    # Initialize an empty DataFrame for the result
    result_df = pd.DataFrame()

    # Iterate through each level and process 'df_' and non-'df_' activities
    for level in sorted(df['Level'].unique()) :
        current_level_df = df[df['Level'] == level]

        # Process 'df_' activities and their immediate non-'df_' next-level activities
        for _,activity_row in current_level_df.iterrows() :
            if activity_row['Activity'].startswith("'df_") :
                # Add 'df_' activities directly to the result
                result_df = result_df.append(activity_row)

                # Get next level non-'df_' activities
                next_level = level + 1
                next_level_activities = df[(df['Level'] == next_level) & (~df['Activity'].str.contains("'df_"))]

                # Check each next-level non-'df_' activity
                for _,next_activity_row in next_level_activities.iterrows() :
                    # Check if the next activity is a deeper part of the current activity's supply chain
                    deeper_activities = df[(df['Level'] > next_level) & (df['Score'] < next_activity_row['Score'])]

                    # Only add if there are no deeper activities
                    if deeper_activities.empty :
                        result_df = result_df.append(next_activity_row)

    # Sort and reset index for the result DataFrame
    result_df = result_df.sort_values(by=['Level','Score'],ascending=[True,False]).reset_index(drop=True)

    return result_df


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

    # Convert to DataFrame
    process_df = pd.DataFrame(process_data)
    print(process_df)

    return process_df




