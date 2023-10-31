import pandas as pd
from rsc.lithium_production.licarbonate_processes import *
import bw2data as bd
from rsc.Brightway2.setting_up_db_env import database_environment

def create_inventory_map(abbrev_loc) :
    inventory_map = {
        "market for hydrochloric acid, without water, in 30% solution state": "chemical_HCl",
        "sodium hydroxide to generic market for neutralising agent": "chemical_NaOH",
        "market for soda ash, light": "chemical_sodaash",
        "market for limestone, crushed, washed": "chemical_limestone",
        "market for quicklime, milled, packed": "chemical_lime",
        "market for cationic resin": "chemical_adsorbent",
        "market for electricity, high voltage": "elec_",
        "heat production, natural gas, at industrial furnace >100kW": "E_",
        "market for hazardous waste, for underground deposit": "waste_solid",
        "market for wastewater, average": "waste_liquid",
        "market for steam, in chemical industry": "steam",
        "Lithium": "m_Li",
        "Sodium": "waste_Na",
        "Chlorine": "waste_Cl",
        "Heat, waste": "waste_heat",
        f"Water_{abbrev_loc}": "water"
    }
    return inventory_map


def change_exchanges_in_database(eff, Li_conc, site_name, abbrev_loc, dict_results) :
    inventory_map = create_inventory_map(abbrev_loc)
    # Selecting the specific dataframe based on Li_conc and eff
    selected_dataframe = dict_results[eff][Li_conc]['data_frames']

    # Assessing Brightway2 database
    site_db = bd.Database(site_name)

    for act in site_db :
        act_name = act['name']

        if act_name.startswith('df_') :
            act_name = act_name[3 :]

        # Filtering the dataframe based on the process name in the "Variable" column "
        if act_name in selected_dataframe:
            filtered_df = selected_dataframe[act_name]

            # Iterating over the exchanges of the activity
            for exc in act.exchanges() :
                exc_name = exc.input['name']
                exc_type = exc.get('type', 'Type not specified')

                #Checking if the exchange needs to be updated
                if exc_name in inventory_map.keys():

                    # Variable_name should get the according value from the dictionary
                    variable_name = inventory_map[exc_name]
                    new_value = filtered_df[filtered_df['Variables'].str.startswith(variable_name)]['per kg'].iloc[0]

                    # Updating the exchange amount
                    exc['amount'] = new_value
                    exc.save()

                elif exc_name.startswith('df_') and exc_type == 'production':
                    new_value = filtered_df[filtered_df['Variables'].str.startswith('m_output')]['per kg'].iloc[0]

                    # Updating the exchange amount
                    exc['amount'] = new_value
                    exc.save()

                elif exc_name.startswith('df_') and exc_type == 'technosphere':
                    new_value = filtered_df[filtered_df['Variables'].str.startswith('m_in')]['per kg'].iloc[0]

                    # Updating the exchange amount
                    exc['amount'] = new_value
                    exc.save()

                else:
                    pass

                #print(f"Activity {act_name} was updated.")
                act.save()
                for activity in site_db :
                    print("Activity:", activity, activity['type'])
                    # Loop through all exchanges for the current activity
                    for exchange in activity.exchanges() :
                        exchange_type = exchange.get('type', 'Type not specified')
                        print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

    print("Database has been updated successfully.")
    return site_db