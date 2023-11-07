import pandas as pd
import numpy as np

def extract_data_2(site_location, abbrev_loc, Li_conc):
    op_data = pd.ExcelFile(r'C:\Users\Schenker\PycharmProjects\pythonProject\data\data_extractionsites.xlsx')
    dat = op_data.parse("Sheet1")
    extracted_database = {}

    if site_location not in dat :
        raise ValueError(f"Location '{site_location}' not found in the data")

    vec_end = [0 for _ in range(15)]
    for i in range(0, 14) :
        vec_end[i] = dat[site_location][i + 19]


    vec_end[0] = Li_conc


    # Use the provided abbreviation for the dictionary key
    extracted_database[abbrev_loc] = {
        f"production" : dat[site_location][0],  # Production of lithium carbonate [kg/yr]
        f"operating_days" : dat[site_location][1],  # Operational days per year
        f"lifetime" : dat[site_location][2],  # Expected time of mining activity [yr]
        f"brine_vol" : dat[site_location][3],  # Brine pumped to the surface [L/s]
        f"freshwater_vol" : dat[site_location][4],  # Fresh water pumped to the surface at evaporation ponds [L/s]
        f"Li_efficiency" : dat[site_location][13],  # Overall Li efficiency
        f"elevation" : dat[site_location][15],  # Elevation of mine site
        f"boilingpoint_process" : dat[site_location][16],  # Boiling point at processing plant [°C]
        f"annual_airtemp" : dat[site_location][17],  # Annual air temperature [°C]
        f"density_brine" : dat[site_location][18],  # Density of initial brine [g/cm3]
        f"vec_end" : vec_end
        }


    return extracted_database



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

