import bw2data as bd
import bw2io as bi
from rsc.lithium_production.processes import loop_functions


def find_activity_by_name_and_location(name, ei_name, location) :
    if ei_name not in bd.databases :
        raise ValueError(f"Database {ei_name} does not exist.")

    ei_reg = bd.Database(ei_name)
    new_act = [act for act in ei_reg if act['name'] == str(name) and act['location'] == location]

    if not new_act :
        raise ValueError(f"No activity found with name '{name}' and location '{location}' in database '{ei_name}'.")

    return new_act

def find_bio_flow_by_name_and_category(name, database, categories):
    bio_flow = [bio_flow for bio_flow in database if bio_flow['name'] == str(name)
                and bio_flow['categories'] == categories][0]
    print(bio_flow)
    return bio_flow



def check_database(database_name, country_location, elec_location, eff, Li_conc, op_location, abbrev_loc, ei_name, biosphere):
    ei_reg = bd.Database(ei_name)
    bio= bd.Database(biosphere)
    if database_name not in bd.databases :
        print(f"{database_name} does not exist.")

        # create bd.database
        db = bd.Database(database_name)
        db.register()
        dfs, _, _ = loop_functions(eff, Li_conc, op_location, abbrev_loc)  # dfs is a list of DataFrames

        # Required activities from ecoinvent and biosphere3

        elec_search = find_activity_by_name_and_location("market for electricity, high voltage", ei_name,
                                                         elec_location)
        print(elec_search)
        wastewater_search = find_activity_by_name_and_location("market for wastewater, average", ei_name, "RoW")
        bio_search = find_bio_flow_by_name_and_category("Water, unspecified natural origin", bio,
                                                        ("natural resource", "in ground"))
        heat_search = find_activity_by_name_and_location("heat production, natural gas, at industrial furnace >100kW",
                                                         ei_name, "RoW")

        chemical_map = {
            "HCl" : {
                "activity_name" : "market for hydrochloric acid, without water, in 30% solution state",
                "location" : "RoW"},
            "NaOH" : {
                "activity_name" : "sodium hydroxide to generic market for neutralising agent",
                "location" : "GLO"},
            "Soda ash" : {
                "activity_name" : "market for soda ash, light",
                "location" : "GLO"},
            "limestone" : {
                "activity_name" : "market for limestone, crushed, washed",
                "location" : "RoW"},
            "lime" : {
                "activity_name" : "market for quicklime, milled, packed",
                "location" : "RoW"},
            "adsorbent" : {
                "activity_name" : "market for cationic resin",
                "location" : "RoW"}
            }

        # Loop over each index of dfs
        for i in range(len(dfs)) :
            df = dfs[i]  # Current DataFrame
            prev_df = dfs[i - 1] if i > 0 else None  # Previous DataFrame or None if current is the first one

            # Get all unique m_output entries
            m_outputs = df[df['Variables'].str.contains('m_output_df_')]
            print(m_outputs)

            # For each m_output entry, create an activity and its exchanges
            for _, m_output_row in m_outputs.iterrows() :
                # Extract process name from the "Variables" column
                activity_name = m_output_row["Variables"].split('m_output_')[1]

                new_act = db.new_activity(amount=1, code=activity_name, name=activity_name, unit="kilogram",
                                          location=country_location)
                new_act.save()
                print(f"Created {activity_name} activity.")

                # Add exchanges for the activity
                # Filter dataframe to get rows related to this activity's process
                exchanges_df = df[df['Variables'].str.contains(activity_name)][1 : :]

                # Loop over each row in the filtered dataframe
                for _, exchange_row in exchanges_df.iterrows() :
                    if exchange_row['Variables'] == f"m_in_{activity_name}" :
                        # If you want to do something with the previous DataFrame
                        if prev_df is not None :
                            # Extract the activity name from prev_df, assuming the name can be derived similarly
                            prev_m_output_row = prev_df[prev_df['Variables'].str.contains('m_output_df_')].iloc[0]
                            prev_activity_name = prev_m_output_row["Variables"].split('m_output_')[1]
                            # Get the previously created activity from the database using the extracted name
                            prev_act = next((act for act in db if act['name'] == prev_activity_name), None)
                            print(prev_act)
                            # Create the exchange
                            new_act.new_exchange(input=prev_act.key, amount=exchange_row['Value'], unit="kilogram",
                                                 type="technosphere").save()
                            print(f"Created exchange for {activity_name} activity.")
                        else :
                            pass

                    elif exchange_row['Variables'] == f"elec_{activity_name}" :
                        new_act.new_exchange(input=elec_search.key, amount=exchange_row['Value'], unit="kilowatt hour",
                                             type="technosphere").save()
                        print(f"Created exchange for {activity_name} activity.")

                    elif exchange_row['Variables'].startswith(f"water_") :
                        act_search = [act for act in db if act['name'] == f'Water_{abbrev_loc}'][0]
                        if act_search is None :
                            water_act = db.new_activity(amount=1, code=f"Water_{abbrev_loc}",
                                                        name=f"Water_{abbrev_loc}",
                                                        unit="kilogram", location=country_location,
                                                        type="production")
                            water_act.save()
                            # act_search = [act for act in ei_name if act['name'] == "market for electricity, high voltage"
                            #              and act['location'] == country_location][0]
                            water_act.new_exchange(input=elec_search.key, amount=0.007206, location=country_location,
                                                   unit="kilowatt hour", type="technosphere").save()

                            # act_search = [act for act in ei_name if act['name'] == "market for wastewater, average" and
                            #              act['location'] == "RoW"][0]
                            water_act.new_exchange(input=wastewater_search.key, amount=-0.00025, location="RoW",
                                                   type="technosphere", unit="cubic meter").save()

                            # bio_search = [bio_act for bio_act in bio_name if bio_act['name'] == "Water, unspecified natural origin"]
                            water_act.new_exchange(input=bio_search.key, amount=0.00025, unit="cubic meter",
                                                   type="biosphere",
                                                   categories=("natural resource", "in ground")).save()

                            print(f"Created Water_{abbrev_loc} activity.")
                        else :
                            new_act.new_exchange(input=act_search.key, amount=exchange_row['Value'], unit="kilogram",
                                                 type="technosphere").save()
                            print(f"Created exchange for {activity_name} activity.")

                    elif exchange_row['Variables'].startswith(f"E_") :
                        new_act.new_exchange(input=heat_search.key, amount=exchange_row['Value'], unit="megajoule",
                                             type="technosphere").save()
                        print(f"Created exchange for {activity_name} activity.")


                    elif "chemical_" in exchange_row['Variables'] :

                        for chem, details in chemical_map.items() :

                            if chem in exchange_row['Variables'] :
                                act_search = [act for act in db if
                                              act['name'] == details['activity_name'] and act['location'] == details[
                                                  'location']][0]

                                new_act.new_exchange(input=act_search.key, amount=exchange_row['Value'],
                                                     unit="kilogram", type="technosphere").save()
                                break
















                        else :
                            # Handle the case where there is no previous DataFrame (i.e., current df is the first one)
                            pass




    else :

        print(f"{database_name} already exists.")
        pass
