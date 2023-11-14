import pandas as pd
import numpy as np


def extract_data(site_location, abbrev_loc, Li_conc) :
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

    vec_ini = [value if pd.notna(value) else np.nan for value in
               site_data.values[8 :24]]
    vec_end = [value if pd.notna(value) else np.nan for value in site_data.values[26 :42]]

    vec_ini[0] = Li_conc

    # Create a dictionary for the extracted data
    extracted_database = {
        abbrev_loc : {
            "deposit_type" : site_data["deposit_type"],
            "country_location" : site_data["country_location"],
            "elevation" : site_data["elevation"],
            "annual_airtemp" : site_data["annual_airtemp (processing)"],
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


    if np.isnan(extracted_database[abbrev_loc]['well_depth_freshwater']):
        extracted_database[abbrev_loc]['well_depth_freshwater'] = site_data['well_depth_brine']

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

