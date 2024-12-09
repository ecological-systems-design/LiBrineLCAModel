import pandas as pd
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
import bw2data as bd
from src.BW2_calculations.setting_up_db_env import database_environment


def create_inventory_map(abbrev_loc) :

    if abbrev_loc == "Ola":
        heat_act = "heat and power co-generation, natural gas, 1MW electrical, lean burn"
        elec_act = heat_act
    else:
        heat_act = "heat production, natural gas, at industrial furnace >100kW"
        elec_act = "market for electricity, high voltage"

    inventory_map = {
        "market for hydrochloric acid, without water, in 30% solution state": "chemical_HCl",
        "sodium hydroxide to generic market for neutralising agent": "chemical_NaOH",
        "market for soda ash, light": "chemical_sodaash",
        "market for limestone, crushed, washed": "chemical_limestone",
        "market for quicklime, milled, packed": "chemical_lime",
        "market for cationic resin": "chemical_adsorbent",
        elec_act: "elec_",
        heat_act: "E_",
        "market for hazardous waste, for underground deposit": "waste_solid",
        "treatment of waste gypsum, inert material landfill": "waste_solid",
        f"waste_liquid_{abbrev_loc}": "waste_liquid",
        "market for steam, in chemical industry": "steam",
        "Lithium": "m_Li",
        "Sodium": "waste_Na",
        "Chlorine": "waste_Cl",
        "Heat, waste": "waste_heat",
        f"Water_{abbrev_loc}": "water",
        "treatment of spent solvent mixture, hazardous waste incineration": "waste_organicsolvent",
        "machine operation, diesel, >= 74.57 kW, high load factor": "diesel_machine",
        "treatment of salt tailing from potash mine, residual material landfill": "waste_salt",
        "transport, freight, lorry >32 metric ton, EURO3": "transport",
        "Occupation, mineral extraction site": "land_occupation",
        "Transformation, from unknown": "land_transform_unknown",
        "Transformation, to mineral extraction site": "land_transform_minesite",
        "market for calcium chloride": "chemical_calciumchloride",
        "market for solvent, organic": "chemical_organicsolvent",
        "market for sulfuric acid": "chemical_sulfuricacid"

    }
    return inventory_map


def change_exchanges_in_database(eff, Li_conc, site_name, abbrev_loc, dict_results) :
    inventory_map = create_inventory_map(abbrev_loc)
    # Selecting the specific dataframe based on Li_conc and eff
    selected_dataframe = dict_results[eff][Li_conc]['data_frames']
    print(f'Efficiency: {eff}, Li_conc: {Li_conc}')
    print(selected_dataframe)

    # Assessing BW2_calculations database
    site_db = bd.Database(site_name)

    # Match the activities with dataframe names
    matched_activities = match_activities(site_db,selected_dataframe)

    for act_name,act in matched_activities.items() :
        print("Processing Activity:",act['name'])
        filtered_df = selected_dataframe[act_name]

        # Iterating over the exchanges of the activity
        for exc in act.exchanges() :
            exc_name = exc.input['name']
            exc_type = exc.get('type','Type not specified')

            # Checking if the exchange needs to be updated
            if exc_name in inventory_map.keys() :
                if exc_name == "heat and power co-generation, natural gas, 1MW electrical, lean burn" :
                    exc_unit = exc.get('unit','Unit not specified')
                    if exc_unit == "megajoule" :
                        variable_name = "E_"
                        filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith(variable_name)]
                        new_value = filtered_var_df['per kg'].iloc[0]
                        exc['amount'] = new_value
                        exc.save()
                    elif exc_unit == "kilowatt hour" :
                        variable_name = "elec_"
                        filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith(variable_name)]
                        new_value = filtered_var_df['per kg'].iloc[0]
                        exc['amount'] = new_value
                        exc.save()
                else:

                    # Variable_name should get the according value from the dictionary
                    variable_name = inventory_map[exc_name]
                    print(variable_name)

                    # Check if filtered DataFrame is not empty
                    filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith(variable_name)]
                    if not filtered_var_df.empty :
                        if variable_name == f"waste_liquid" :
                            new_value = -filtered_var_df['per kg'].iloc[0] / 1000
                            print(f'Is updated: {new_value}')
                        else :
                            new_value = filtered_var_df['per kg'].iloc[0]

                        # Check if old value and new value in exchange are the same. If yes, print a message
                        if exc['amount'] == new_value :
                            print(f'.')
                        else :
                            # Updating the exchange amount
                            exc['amount'] = new_value
                            exc.save()
                            print(f'Updated {exc_name} from {exc["amount"]} to {new_value}')
                    else :
                        print(f'Variable name {variable_name} not found in filtered DataFrame for activity {act_name}')

            elif exc_name.startswith('df_') and exc_type == 'production' :
                filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith('m_output')]
                if not filtered_var_df.empty :
                    new_value = filtered_var_df['per kg'].iloc[0]
                    # Check if old value and new value in exchange are the same. If yes, print a message
                    if exc['amount'] == new_value :
                        print(f'.')
                    else :
                        # Updating the exchange amount
                        exc['amount'] = new_value
                        exc.save()
                        print(f'Updated {exc_name} from {exc["amount"]} to {new_value}')
                else :
                    print(f'm_output not found in filtered DataFrame for activity {act_name}')

            elif exc_name.startswith('df_') and exc_type == 'technosphere' :
                filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith('m_in')]
                if not filtered_var_df.empty :
                    new_value = filtered_var_df['per kg'].iloc[0]
                    # Check if old value and new value in exchange are the same. If yes, print a message
                    if exc['amount'] == new_value :
                        print(f'.')
                    else :
                        # Updating the exchange amount
                        exc['amount'] = new_value
                        exc.save()
                        print(f'Updated {exc_name} from {exc["amount"]} to {new_value}')
                else :
                    print(f'm_in not found in filtered DataFrame for activity {act_name}')

            else :
                print(f'Exchange not found:',exc_name,exc_type)

            # Print activity update status
            act.save()
    # for activity in site_db :
    #     print("Activity:", activity, activity['type'])
    #     # Loop through all exchanges for the current activity
    #     for exchange in activity.exchanges() :
    #         exchange_type = exchange.get('type', 'Type not specified')
    #         print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

    print("Database has been updated successfully.")
    return site_db


def normalize_name(name) :
    """
    Normalize the name by removing the prefix 'df_', suffixes, and underscores.
    """
    # Remove prefix 'df_' if it exists
    if name.startswith('df_') :
        name = name[3 :]
    # Replace underscores with nothing
    name = name.replace('_','')
    # Return the normalized name
    return name.lower()


def extract_base_name(variable) :
    """
    Extract the base name from a variable, such as 'm_output_df_rotary_dryer' to 'rotary_dryer'.
    """
    parts = variable.split('_')
    if len(parts) > 2 :
        return '_'.join(parts[2 :])
    return variable

def match_activities(site_db,dataframe) :
    """
    Match activities in the site_db with the names in the dataframe.
    """
    matched_activities = {}

    for df_name in dataframe :
        # Normalize the dataframe name
        normalized_df_name = normalize_name(df_name[:-2])  # Remove the '_1' suffix
        for activity in site_db :
            # Normalize the activity name
            activity_name = activity['name']
            normalized_activity = normalize_name(activity_name)

            if normalized_activity == normalized_df_name :
                matched_activities[df_name] = activity
                break

    return matched_activities


def change_exchanges_in_database_sensitivity(param,value,site_name,abbrev_loc,dict_results) :
    inventory_map = create_inventory_map(abbrev_loc)

    # Selecting the specific dataframe based on the parameter and its value
    if param not in dict_results or value not in dict_results[param] :
        raise KeyError(f"Key '{param}|{value}' not found in dict_results")
    print(param,value)
    selected_dataframe = dict_results[param][value]['data_frames']
    print("Selected Dataframe:",selected_dataframe)

    # Assessing BW2_calculations database
    site_db = bd.Database(site_name)

    # Match the activities with dataframe names
    matched_activities = match_activities(site_db,selected_dataframe)

    for act_name,act in matched_activities.items() :
        print("Processing Activity:", act['name'])
        filtered_df = selected_dataframe[act_name]

        # Iterating over the exchanges of the activity
        for exc in act.exchanges() :
            exc_name = exc.input['name']
            exc_type = exc.get('type','Type not specified')

            # Checking if the exchange needs to be updated
            if exc_name in inventory_map.keys() :

                if exc_name == "heat and power co-generation, natural gas, 1MW electrical, lean burn" :
                    exc_unit = exc.get('unit','Unit not specified')
                    if exc_unit == "megajoule" :
                        variable_name = "E_"
                        filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith(variable_name)]
                        new_value = filtered_var_df['per kg'].iloc[0]
                        exc['amount'] = new_value
                        exc.save()
                    elif exc_unit == "kilowatt hour" :
                        variable_name = "elec_"
                        filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith(variable_name)]
                        new_value = filtered_var_df['per kg'].iloc[0]
                        exc['amount'] = new_value
                        exc.save()
                else:
                    # Variable_name should get the according value from the dictionary
                    variable_name = inventory_map[exc_name]

                    # Check if filtered DataFrame is not empty
                    filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith(variable_name)]
                    if not filtered_var_df.empty :
                        if variable_name == f"waste_liquid":
                            new_value = -filtered_var_df['per kg'].iloc[0]/1000
                            print(f'Is updated: {new_value}')
                        else:
                            new_value = filtered_var_df['per kg'].iloc[0]

                        # Check if old value and new value in exchange are the same. If yes, print a message
                        if exc['amount'] == new_value :
                            print(f'.')
                        else :
                            # Updating the exchange amount
                            exc['amount'] = new_value
                            exc.save()
                            print(f'Updated {exc_name} from {exc["amount"]} to {new_value}')
                    else :
                        print(f'Variable name {variable_name} not found in filtered DataFrame for activity {act_name}')

            elif exc_name.startswith('df_') and exc_type == 'production' :
                filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith('m_output')]
                if not filtered_var_df.empty :
                    new_value = filtered_var_df['per kg'].iloc[0]
                    # Check if old value and new value in exchange are the same. If yes, print a message
                    if exc['amount'] == new_value :
                        print(f'.')
                    else :
                        # Updating the exchange amount
                        exc['amount'] = new_value
                        exc.save()
                        print(f'Updated {exc_name} from {exc["amount"]} to {new_value}')
                else :
                    print(f'm_output not found in filtered DataFrame for activity {act_name}')

            elif exc_name.startswith('df_') and exc_type == 'technosphere' :
                filtered_var_df = filtered_df[filtered_df['Variables'].str.startswith('m_in')]
                if not filtered_var_df.empty :
                    new_value = filtered_var_df['per kg'].iloc[0]
                    # Check if old value and new value in exchange are the same. If yes, print a message
                    if exc['amount'] == new_value :
                        print(f'.')
                    else :
                        # Updating the exchange amount
                        exc['amount'] = new_value
                        exc.save()
                        print(f'Updated {exc_name} from {exc["amount"]} to {new_value}')
                else :
                    print(f'm_in not found in filtered DataFrame for activity {act_name}')

            else :
                print(f'Exchange not found:',exc_name,exc_type)

            # Print activity update status
            act.save()

    # for activity in site_db :
    #     print("Activity:",activity,activity['type'])
    #     act_search = [act for act in site_db if act['name'] == f"waste_liquid_{abbrev_loc}"][0]
    #     for exchange in act_search.exchanges():
    #         exchange_type = exchange.get('type','Type not specified')
    #         print("\tExchange:",exchange.input,"->",exchange.amount,exchange.unit,exchange_type, exchange.as_dict())
        # Loop through all exchanges for the current activity
        # for exchange in activity.exchanges() :
        #     exchange_type = exchange.get('type','Type not specified')
        #     print("\tExchange:",exchange.input,"->",exchange.amount,exchange.unit,exchange_type)

    print("Database has been updated successfully.")
    return site_db
