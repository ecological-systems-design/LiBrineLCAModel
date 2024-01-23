import pandas as pd
import numpy as np

#Default values for non-critical values of a specific site
standard_values = {
    "evaporation_rate" : np.nan,
    "boilingpoint_process" : np.nan,
    "density_brine" : 1.2,
    "density_enriched_brine" : 1.3,
    "production" : 40000000,
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
    "quicklime_reported" : 1,
    "diesel_reported" : 0,
    "diesel_consumption" : np.nan,
    "motherliq_reported" : 0
    }

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

def find_closest_valid_site(current_site_lat, current_site_lon, op_data, vec_indices, offset):
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



def extract_data(site_location, abbrev_loc, Li_conc = None) :
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
    critical_keys = ['deposit_type', 'country_location', 'elevation', 'annual_airtemp', 'longitude', 'latitude']
    for key in critical_keys :
        if pd.isna(site_data[key]) :
            raise ValueError(f"Critical value missing for '{key}' in the data for location '{site_location}'")

    # Retrieve the deposit type
    deposit_type = site_data.get("deposit_type")

    # Define nan_indices based on deposit_type
    if deposit_type == "salar" :
        nan_indices_ini = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # Indices for "salar"
    elif deposit_type == "geothermal" :
        nan_indices_ini = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # Indices for "geothermal"
    else :
        raise ValueError(f"Unknown deposit type '{deposit_type}' for location '{site_location}'")

    # Replace NaN values in non-critical data with standard values
    for key, value in site_data.items() :
        if key not in critical_keys and pd.isna(value) :
            site_data[key] = standard_values.get(key, np.nan)

    vec_ini = [value if pd.notna(value) else np.nan for value in
               site_data.values[10 :26]]
    vec_end = [value if pd.notna(value) else np.nan for value in site_data.values[28 :44]]

    if Li_conc is not None:
        vec_ini[0] = Li_conc

    print(f"vec_ini before: {vec_ini}")
    if any(pd.isna(vec_ini[i]) for i in nan_indices_ini) :
        closest_site_data = find_closest_valid_site(site_data['latitude'], site_data['longitude'], dat, nan_indices_ini, 10)
        if closest_site_data is not None :
            for i in nan_indices_ini :
                offset_index = i + 10  # Apply the offset here
                if pd.isna(vec_ini[i]) :
                    vec_ini[i] = closest_site_data.iloc[
                        offset_index]  # Use the offset index to access data in closest_site_data
    print(f"vec_ini after: {vec_ini}")

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

    # Create a dictionary for the extracted data
    extracted_database = {
        abbrev_loc : {
            "deposit_type" : site_data["deposit_type"],
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
            "production" : site_data["production"],
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
            "motherliq_reported": site_data['motherliq_reported']

            }
        }

    #adaptions to input data
    if np.isnan(extracted_database[abbrev_loc]['well_depth_freshwater']):
        extracted_database[abbrev_loc]['well_depth_freshwater'] = site_data['well_depth_brine']

    if np.isnan(extracted_database[abbrev_loc]['boilingpoint_process']):
        extracted_database[abbrev_loc]['boilingpoint_process'] = boiling_point_at_elevation(extracted_database[abbrev_loc]['elevation'])


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

