import numpy as np
import pandas as pd

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


if __name__ == '__main__' :
    df = preparing_data_recursivecalculation(file_path, category_mapping)
