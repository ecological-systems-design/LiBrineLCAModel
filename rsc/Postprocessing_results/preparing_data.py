import numpy as np
import pandas as pd
import os

file_path = r"C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\recursive_calculation\results_Ata\Salar de Atacama_waterscarcity_0.15.csv"

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
        'Grassroots' : '1 - Exploration - Early stage',
        'Exploration' : '1 - Exploration - Early stage',
        'Target Outline' : '1 - Exploration - Early stage',
        'Commissioning' : '1 - Exploration - Early stage',
        'Prefeas/Scoping' : '1 - Exploration - Early stage',
        'Advanced exploration' : '1 - Exploration - Early stage',
        'Feasibility Started' : '1 - Exploration - Early stage',
        'Reserves Development' : '2 - Exploration - Late stage',
        'Feasibility' : '2 - Exploration - Late stage',  # If Feasibility means Feasibility complete
        'Feasibility complete' : '2 - Exploration - Late stage',
        'Construction started' : '2 - Exploration - Late stage',
        'Construction planned' : '2 - Exploration - Late stage',
        'Preproduction' : '3 - Mine stage',
        'Production' : '3 - Mine stage',
        'Operating' : '3 - Mine stage',
        'Satellite' : '3 - Mine stage',
        'Expansion' : '3 - Mine stage',
        'Limited Production' : '3 - Mine stage',
        'Residual Production' : '3 - Mine stage'
        }

    # Extracting the relevant columns: Site name, abbreviation, and country location, ini_Li, Li_efficiency

    sites_info = {}

    for site, row in transposed_data.iterrows() :
        activity_status = row.get("activity_status",None)
        site_info = {
            "abbreviation" : row[ "abbreviation" ],
            "country_location" : row[ "country_location" ],
            "ini_Li" : row.get("ini_Li", None),
            "Li_efficiency" : row.get("Li_efficiency", None),
            "deposit_type" : row.get("deposit_type", None),
            "technology_group": row.get("technology_group", None),
            "activity_status": row.get("activity_status", None),
            "activity_status_order" : activity_status_order.get(activity_status,'4 - Other')
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
                    print(site_abbreviation)
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