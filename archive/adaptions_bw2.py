import bw2data as bd
from src.BW2_calculations.lithium_site_db import create_database


def find_closest_valid_site(current_site_lat, current_site_lon, op_data, vec_ini_indices):
    if 'latitude' not in op_data.columns or 'longitude' not in op_data.columns:
        raise ValueError("Required columns 'latitude' and/or 'longitude' are missing in the data")

    closest_distance = float('inf')
    closest_site_data = None

    for index, row in op_data.iterrows():
        if index == current_site_lat:  # Skip the current site
            continue

        site_lat, site_lon = row['latitude'], row['longitude']
        distance = haversine((current_site_lat, current_site_lon), (site_lat, site_lon))

        # Adjusted index calculation
        adjusted_indices = [i + 10 for i in vec_ini_indices]
        if not pd.isna(row.iloc[adjusted_indices]).any():
            print(f"Checking site at index {index}: distance = {distance}, closest so far = {closest_distance}")
            if distance < closest_distance:
                closest_distance = distance
                closest_site_data = row
                print(f"New closest site found at index {index} with distance {distance}")

    return closest_site_data
