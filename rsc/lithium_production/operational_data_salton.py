import pandas as pd

def extract_data(location, abbrev_loc, Li_conc):
    op_data = pd.ExcelFile(r'C:\Users\Schenker\PycharmProjects\pythonProject\data\data_extractionsites.xlsx')
    dat = op_data.parse("Sheet1")
    extracted_database = {}

    if location not in dat :
        raise ValueError(f"Location '{location}' not found in the data")

    vec_end = [0 for _ in range(15)]
    for i in range(0, 14) :
        vec_end[i] = dat[location][i + 19]


    vec_end[0] = Li_conc


    # Use the provided abbreviation for the dictionary key
    extracted_database[abbrev_loc] = {
        f"production" : dat[location][0],  # Production of lithium carbonate [kg/yr]
        f"operating_days" : dat[location][1],  # Operational days per year
        f"lifetime" : dat[location][2],  # Expected time of mining activity [yr]
        f"Brine_vol" : dat[location][3],  # Brine pumped to the surface [L/s]
        f"Freshwater_vol" : dat[location][4],  # Fresh water pumped to the surface at evaporation ponds [L/s]
        f"Li_efficiency" : dat[location][13],  # Overall Li efficiency
        f"elevation" : dat[location][15],  # Elevation of mine site
        f"boilingpoint_process" : dat[location][16],  # Boiling point at processing plant [°C]
        f"annual_airtemp" : dat[location][17],  # Annual air temperature [°C]
        f"density_brine" : dat[location][18],  # Density of initial brine [g/cm3]
        f"vec_end" : vec_end
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

