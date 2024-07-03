import pandas as pd
import numpy as np
import xarray as xr
import os

#Default values for non-critical values of a specific site
standard_values = {
    "evaporation_rate" : np.nan,
    "boilingpoint_process" : np.nan,
    "density_brine" : 1.2,
    "density_enriched_brine" : 1.3,
    "production" : 10000000,
    "operating_days" : 0.9 * 365,
    "lifetime" : 30,
    "brine_vol" : np.nan,
    "freshwater_reported" : 0,
    "freshwater_vol" : np.nan,
    "Li_efficiency" : 0.4,
    "number_wells" : 10,
    "well_depth_brine" : 50,
    "well_depth_freshwater" : np.nan,
    "distance_to_processing" : 0,
    "second_Li_enrichment_reported" : 0,
    "second_Li_enrichment" : np.nan,
    "quicklime_reported" : 0,
    "diesel_reported" : 0,
    "diesel_consumption" : np.nan,
    "motherliq_reported" : 0
    }

#make a dict of all classes in licarbonate_processes.py
process_required_concentrations_dict = {
    "evaporation_ponds" : [0],
    "B_removal_organicsolvent" : [7, 6],
    "CaMg_removal_sodiumhydrox" : [4, 5, 14, 13],
    "Mg_removal_sodaash" : [5],
    "sulfate_removal_calciumchloride": [6],
    "SiFe_removal_limestone": [8, 11],
    "MnZn_removal_lime": [10, 12]
    }


def convert_mg_L_to_wt_percent(values,density,sum_threshold=100) :
    """
    Converts a list of values from mg/L to weight percent, if they are not already in weight percent.

    Parameters:
    values (list): List of values in mg/L or weight percent.
    density (float): Density of the solution in g/mL.
    sum_threshold (float): Threshold to distinguish between mg/L and weight percent.

    Returns:
    list: List of values in weight percent.
    """
    density = float(density)
    wt_percent_values = []

    # Convert values to a numpy array to handle NaN values
    values_array = np.array(values,dtype=np.float64)

    # Calculate the sum ignoring NaN values
    total_sum = np.nansum(values_array)

    # Check if the values are likely in mg/L based on the sum
    if total_sum > sum_threshold :
        print("Values are in mg/L, converting to weight percent")
        for value in values_array :
            # Skip NaN values
            if np.isnan(value) :
                wt_percent_values.append(np.nan)
                continue

            # Perform the calculation with numeric types
            wt_percent = (value / 1000) / (density * 1000) * 100
            wt_percent_values.append(wt_percent)
    else :
        print("Values are already in weight percent")
        wt_percent_values = values

    return wt_percent_values

def boiling_point_at_elevation(elevation_meters):
    """
    Calculate the boiling point of water at a given elevation.

    :param elevation_meters: Elevation in meters.
    :return: Boiling point of water at the given elevation in degrees Celsius.
    """
    # Standard boiling point of water at sea level in Celsius
    boiling_point_sea_level = 100

    # Atmospheric pressure decreases approximately by 0.1 kPa for each 10 meters increase in elevation
    # The following is a simplified formula and is an approximation
    atmospheric_pressure = 101.3 - (0.1 * elevation_meters / 10)

    # Calculate boiling point adjustment based on pressure
    # This is an approximation based on the Clausius-Clapeyron relation
    boiling_point_adjustment = (boiling_point_sea_level - 100) * 0.0065 / 0.1

    # Adjust boiling point based on current atmospheric pressure
    boiling_point = boiling_point_sea_level - boiling_point_adjustment * (101.3 - atmospheric_pressure)

    return boiling_point


def haversine(coord1, coord2):
    R = 6371  # Earth radius in km
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance

def find_closest_valid_site_brinechemistry(current_site_lat, current_site_lon, op_data, vec_indices, offset):
    if 'latitude' not in op_data.columns or 'longitude' not in op_data.columns:
        raise ValueError("Required columns 'latitude' and/or 'longitude' are missing in the data")

    closest_distance = float('inf')
    closest_site_data = None

    for index, row in op_data.iterrows():
        if index == current_site_lat:  # Skip the current site
            continue

        site_lat, site_lon = row['latitude'], row['longitude']
        distance = haversine((current_site_lat, current_site_lon), (site_lat, site_lon))

        # Adjusted index calculation using the offset
        adjusted_indices = [i + offset for i in vec_indices if i + offset < len(row)]

        if not pd.isna(row.iloc[adjusted_indices]).any():
            print(f"Checking site at index {index}: distance = {distance}, closest so far = {closest_distance}")
            if distance < closest_distance:
                closest_distance = distance
                closest_site_data = row
                print(f"New closest site found at index {index} with distance {distance}")

    return closest_site_data

def find_closest_valid_site_evaporation(current_site_lat, current_site_lon, op_data):
    if 'latitude' not in op_data.columns or 'longitude' not in op_data.columns:
        raise ValueError("Required columns 'latitude' and/or 'longitude' are missing in the data")

    closest_distance = float('inf')
    closest_site_data = None

    for index, row in op_data.iterrows():
        if index == current_site_lat:  # Skip the current site
            continue

        site_lat, site_lon = row['latitude'], row['longitude']
        distance = haversine((current_site_lat, current_site_lon), (site_lat, site_lon))

        if not pd.isna(row['evaporation_rate']):
            print(f"Checking site at index {index}: distance = {distance}, closest so far = {closest_distance}")
            if distance < closest_distance:
                closest_distance = distance
                closest_site_data = row
                print(f"New closest site found at index {index} with distance {distance}")

    return closest_site_data

def mean_annual_temperature(lat, lon, dataset):
    """
    Calculate the mean annual temperature for a given latitude and longitude.

    Parameters:
    lat (float): Latitude of the location.
    lon (float): Longitude of the location.
    dataset (xarray.Dataset): The dataset containing temperature data.

    Returns:
    float: Mean annual temperature for the specified location.
    """
    # Select the temperature data for the nearest location
    temp_data = dataset['tas'].sel(lat=lat, lon=lon, method='nearest')

    # Calculate the mean temperature across all time points
    mean_temp = temp_data.mean(dim='time')

    return mean_temp.values  # Return the mean temperature value

def update_required_concentrations( process_sequence, vec_end, vec_ini):

    process_update_status = {}
    li_index = process_sequence.index('Li_adsorption') if 'Li_adsorption' in process_sequence else -1

    if li_index != -1:
        # vec_ini == vec_end because the model assumes no concentration in the evaporation ponds
        vec_end = vec_ini
        process_update_status['Li_adsorption'] = 'Updated'


    for process in process_sequence :
        if process in process_required_concentrations_dict :
            required_indices = process_required_concentrations_dict[ process ]
            for i in required_indices :
                if pd.isna(vec_end[ i ]) :
                    ratio = (vec_end[0]/vec_ini[0])*0.1
                    # Apply the rule to update the NaN value
                    vec_end[ i ] = vec_ini[i] * ratio  #worst case that no salt is precipitated
                    process_update_status[ process ] = 'Updated'
                else :
                    process_update_status[ process ] = 'No change'

    return vec_end, process_update_status


def extract_data(site_location, abbrev_loc, Li_conc = None, vec_ini = None) :
    print(f'beginning of function: {vec_ini}')
    # Load the Excel file
    op_data = pd.read_excel(r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\new_file_lithiumsites.xlsx',
                            sheet_name="Sheet1", index_col=0)

    # Transpose the data for easier row (site) access
    dat = op_data.T

    # Check if the site_location exists in the data
    if site_location not in dat.index :
        raise ValueError(f"Location '{site_location}' not found in the data")

    # Access the site's data
    site_data = dat.loc[site_location]

    # Check for NaN in critical values
    critical_keys = ['deposit_type', 'country_location', 'elevation', 'longitude', 'latitude']
    for key in critical_keys :
        if pd.isna(site_data[key]) :
            raise ValueError(f"Critical value missing for '{key}' in the data for location '{site_location}'")

    # Retrieve the deposit type
    deposit_type = site_data.get("deposit_type")
    info_assumption = {"vec_ini": None,
                        "evaporation_rate": None
                        }

    #Calculate the mean annual temperature
    site_data["annual_airtemp"] = mean_annual_temperature(site_data["latitude"], site_data["longitude"],
                                    xr.open_dataset(r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\annual_air_temperature.nc', decode_times=False))
    # Define nan_indices based on deposit_type
    if deposit_type == "salar" :
        nan_indices_ini = [0, 4, 5, 6, 7]  # Indices for "salar"
    elif deposit_type == "geothermal" :
        nan_indices_ini = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # Indices for "geothermal"
    else :
        raise ValueError(f"Unknown deposit type '{deposit_type}' for location '{site_location}'")

    # Replace NaN values in non-critical data with standard values
    for key, value in site_data.items() :
        if key not in critical_keys and pd.isna(value) :
            site_data[key] = standard_values.get(key, np.nan)

    # Extract the initial and final brine chemistry data
    # Use provided vec_ini if available
    if vec_ini is None :
        # Original logic to construct vec_ini from Sheet1
        vec_ini = [ value if pd.notna(value) else np.nan for value in site_data.values[ 13 :29 ] ]
    else:
        vec_ini = convert_mg_L_to_wt_percent(vec_ini, site_data['density_brine'])
        # Calculate the sum of converted wt.% values
        total_wt_percent = sum(vec_ini)

        # Calculate the last value as 100 - SUM(vec_ini_converted) and append it
        last_value = 100 - total_wt_percent
        vec_ini = vec_ini + [ last_value ]

    print(f'vec_ini here: {vec_ini}')

    # Extract the technology type
    technology_type = site_data.get('technology_group') # assuming technology_group is consistent

    # Check if the technology type is 'salar_DLE' or 'geo_DLE'
    if technology_type in ['salar_DLE','geo_DLE'] :
        vec_end = vec_ini
    else :
        vec_end = [value if pd.notna(value) else np.nan for value in site_data.values[31 :47]]


    if Li_conc is not None:
        vec_ini[0] = Li_conc

    if any(pd.isna(vec_ini[i]) for i in nan_indices_ini) :
        print('yes')
        closest_site_data = find_closest_valid_site_brinechemistry(site_data['latitude'], site_data['longitude'], dat, nan_indices_ini, 13)
        if closest_site_data is not None :

            for i in nan_indices_ini :
                offset_index = i + 13  # Apply the offset here
                if pd.isna(vec_ini[i]) :
                    vec_ini[i] = closest_site_data.iloc[
                        offset_index]  # Use the offset index to access data in closest_site_data
                    print(f"Updated vec_ini value at index {i} with value from closest site: {vec_ini[i]}")
                    info_assumption = {"vec_ini": closest_site_data.name}

    print(vec_ini)

    # Convert all elements in vec_ini to floats, replace non-numeric values with 0 or NaN
    vec_ini_float = []
    for item in vec_ini[:-1] :  # Exclude the last item for now
        try :
            vec_ini_float.append(float(item))  # Convert to float
        except ValueError :  # Handle the case where conversion to float fails
            vec_ini_float.append(0)  # Replace with 0 or you can use np.nan

    # Now sum the converted list
    sum_of_others = sum(vec_ini_float)

    # Set the last element of vec_ini
    vec_ini[-1] = 100 - sum_of_others

    # Initialize an empty list to store the process sequence
    process_sequence = [ ]

    # Iterate over the index and value in the Series
    for index, value in site_data.items() :
        # Check if the index starts with 'process_'
        if str(index).startswith('process_') :
            # If the value is not empty or NaN, add the process to the list
            if value and not pd.isna(value) :
                process_sequence.append(value)

    # Update vec_end if there are nan values using the function from above
    vec_end, process_update_status = update_required_concentrations(process_sequence, vec_end,
                                                                    vec_ini)
    print(vec_end)

    if "evaporation_ponds" in process_sequence:
        if pd.isna(site_data["evaporation_rate"]):
            closest_site_data = find_closest_valid_site_evaporation(site_data['latitude'], site_data['longitude'], dat)
            if closest_site_data is not None:
                site_data["evaporation_rate"] = closest_site_data["evaporation_rate"]
                info_assumption["evaporation_rate"] = closest_site_data.name
    else:
        site_data["evaporation_rate"] = 0 # Set to 0 if the process is not in the sequence

    # Create a dictionary for the extracted data
    extracted_database = {
        abbrev_loc : {
            "site_location": site_data.name,
            "deposit_type" : site_data["deposit_type"],
            "technology_group": site_data["technology_group"],
            "country_location" : site_data["country_location"],
            "elevation" : site_data["elevation"],
            "longitude": site_data["longitude"],
            "latitude": site_data["latitude"],
            "annual_airtemp" : site_data["annual_airtemp"],
            "evaporation_rate" : site_data["evaporation_rate"],
            "boilingpoint_process" : site_data["boilingpoint_process"],
            "density_brine" : site_data["density_brine"],
            "vec_ini" : vec_ini,  # Vector with initial brine chemistry data
            "density_enriched_brine" : site_data.get("density_enriched_brine", np.nan),
            "vec_end" : vec_end,  # Vector with enriched brine chemistry data
            "production" : site_data.get("production", np.nan),
            "operating_days" : site_data["operating_days"],
            "lifetime" : site_data["lifetime"],
            "brine_vol" : site_data["brine_vol"],
            "freshwater_reported" : site_data.get("freshwater_reported", np.nan),
            "freshwater_vol" : site_data.get("freshwater_vol", np.nan),
            "Li_efficiency" : site_data["Li_efficiency"],
            "number_wells" : site_data.get("number_wells", np.nan),
            "well_depth_brine" : site_data.get("well_depth_brine", np.nan),
            "well_depth_freshwater" : site_data.get("well_depth_freshwater", np.nan),
            "distance_to_processing" : site_data["distance_to_processing"],
            "second_Li_enrichment_reported": site_data['second_Li_enrichment_reported'],
            "second_Li_enrichment": site_data.get("second_Li_enrichment", np.nan),
            "quicklime_reported": site_data['quicklime_reported'],
            "diesel_reported": site_data['diesel_reported'],
            "diesel_consumption": site_data['diesel_consumption'],
            "motherliq_reported": site_data['motherliq_reported'],
            "process_sequence": process_sequence,
            "ini_Li": vec_ini[0]

            }
        }

    #adaptions to input data
    if np.isnan(extracted_database[abbrev_loc]['well_depth_freshwater']):
        extracted_database[abbrev_loc]['well_depth_freshwater'] = site_data['well_depth_brine']

    if np.isnan(extracted_database[abbrev_loc]['boilingpoint_process']):
        extracted_database[abbrev_loc]['boilingpoint_process'] = boiling_point_at_elevation(extracted_database[abbrev_loc]['elevation'])

    #create a csv file if one does not already exist and save the extracted_database
    # Path to the CSV file
    csv_file_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\extracted_data_all_sites.csv'

    # Convert the extracted_database dictionary to a DataFrame for easier manipulation
    extracted_df = pd.DataFrame.from_dict(extracted_database,orient='index')

    # Check if the CSV file exists
    if os.path.exists(csv_file_path) :
        # Read the existing CSV file
        existing_df = pd.read_csv(csv_file_path,index_col=0)

        # Concatenate the new data with the existing data
        # Assuming you want to add a new row for each site
        updated_df = pd.concat([existing_df,extracted_df],ignore_index=True)

        # Save the updated DataFrame back to the CSV file
        updated_df.to_csv(csv_file_path)
    else :
        # If the file does not exist, save the extracted data as a new CSV file
        extracted_df.to_csv(csv_file_path)


    return extracted_database


def update_config_value(config, key, new_value):
    """
    Update a specific key in the config dictionary with a new value.

    Args:
        config (dict): The configuration dictionary.
        key (str): The key to update.
        new_value: The new value to assign to the key.

    Returns:
        None
    """
    if key in config:
        config[key] = new_value
    else:
        print(f"Key '{key}' not found in the {config} dictionary.")



def convert_to_numeric_old(df, columns):
    for column in columns:
        # Only attempt to replace commas if the column contains string values
        if df[column].dtype == 'object':
            df[column] = df[column].str.replace(',', '')
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df


def convert_to_numeric(df,columns) :
    for column in columns :
        if column in df.columns :
            # Print original values for debugging
            #print(f"Original values in column {column}:\n",df[column].head())

            # Replace commas and convert all values to strings
            df[column] = df[column].astype(str).str.replace(',','')

            # Convert to numeric
            df[column] = pd.to_numeric(df[column],errors='coerce')

            # Print converted values for debugging
            #print(f"Converted values in column {column}:\n",df[column].head())
    return df


def prepare_brine_analyses(file_path,abbrev_loc) :
    # Load and prepare sheet4 for brine analyses
    columns_to_convert = ['ini_Li','ini_Cl','ini_Na','ini_K','ini_Ca','ini_Mg',
                          'ini_SO4','ini_B','ini_Si','ini_As','ini_Mn','ini_Fe','ini_Zn','ini_Sr','ini_Ba','ini_H2O']
    sheet4_df = pd.read_excel(file_path,sheet_name="Sheet4",index_col=0)

    # Drop columns where all elements are NaN
    sheet4_df.dropna(axis=1,how='all',inplace=True)

    # Ensure all columns_to_convert are in the DataFrame, adding them with NaN values if they are missing
    for column in columns_to_convert :
        if column not in sheet4_df.columns :
            sheet4_df[column] = np.nan

    # Filter out 'Unnamed' columns if they exist
    sheet4_df = sheet4_df.loc[:,~sheet4_df.columns.str.contains('^Unnamed')]

    # Print available columns for debugging
    available_columns = sheet4_df.columns.tolist()
    #print("Available columns before conversion:",available_columns)

    # Apply the conversion function
    sheet4_df = convert_to_numeric(sheet4_df,columns_to_convert)

    # Replace non-numeric placeholders with NaN (or other value as needed)
    sheet4_df.replace({'-' : np.nan},inplace=True)

    # Drop rows where all elements are NaN
    sheet4_df.dropna(how='all',inplace=True)

    # Drop rows where the index itself is NaN and convert the index to string
    sheet4_df = sheet4_df[~sheet4_df.index.isna()]
    sheet4_df.index = sheet4_df.index.map(str)

    # Use a boolean mask to filter rows where the index starts with {abbrev_loc}_
    matched_analyses = sheet4_df[sheet4_df.index.to_series().str.startswith(f"{abbrev_loc}_")]


    # Convert matched analyses to a structured format (dictionary or list)
    analyses_dict = {idx : row.tolist() for idx,row in matched_analyses.iterrows()}

    return analyses_dict,available_columns


def generate_range(value,percentage) :
    """Generate a range around a value based on a percentage."""
    lower_bound = value * (1 - percentage)
    upper_bound = value * (1 + percentage)
    return [lower_bound,value,upper_bound]


def define_custom_ranges(extracted_database,abbrev_loc,custom_percentages) :
    site_data = extracted_database[abbrev_loc]

    SENSITIVITY_RANGES_SITE_PARAMS = {
        'annual_airtemp' : generate_range(site_data['annual_airtemp'],custom_percentages.get('annual_airtemp',0.1)),
        'density_brine' : generate_range(site_data['density_brine'],custom_percentages.get('density_brine',0.1)),
        'density_enriched_brine' : generate_range(site_data.get('density_enriched_brine',1.13),
                                                  custom_percentages.get('density_enriched_brine',0.1)),
        'lifetime' : generate_range(site_data['lifetime'],custom_percentages.get('lifetime',0.1)),
        'Li_efficiency' : generate_range(site_data['Li_efficiency'],custom_percentages.get('Li_efficiency',0.1)),
        'brine_vol' : generate_range(site_data['brine_vol'],custom_percentages.get('brine_vol',0.1)),
        'well_depth_brine' : generate_range(site_data.get('well_depth_brine',1500),
                                            custom_percentages.get('well_depth_brine',0.1)),
        'distance_to_processing' : generate_range(site_data['distance_to_processing'],
                                                  custom_percentages.get('distance_to_processing',0.1)),
        'production' : generate_range(site_data.get('production',1),custom_percentages.get('production',0.1)),
        'evaporation_rate' : generate_range(site_data.get('evaporation_rate',0),
                                            custom_percentages.get('evaporation_rate',0.1))
        }

    return SENSITIVITY_RANGES_SITE_PARAMS





