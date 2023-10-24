import bw2data as bd
from rsc.lithium_production.licarbonate_processes import calculate_processingsequence


def find_activity_by_name_and_location(name, ei_name, location) :
    if ei_name not in bd.databases :
        raise ValueError(f"Database {ei_name} does not exist.")

    ei_reg = bd.Database(ei_name)
    return next((act for act in ei_reg if act['name'] == str(name) and act['location'] == location), None)


def find_bio_flow_by_name_and_category(name, database, categories) :
    bio_flow = next((bio_flow for bio_flow in database if bio_flow['name'] == str(name)
                     and bio_flow['categories'] == categories), None)
    print(bio_flow)
    return bio_flow


def create_exchanges(activity, exchanges) :
    for key, amount, unit, type_, location, categories in exchanges :
        activity.new_exchange(input=key, amount=amount, unit=unit, type=type_,
                              location=location, categories=categories).save()


def check_database(database_name, country_location, eff, Li_conc, op_location, abbrev_loc, ei_name,
                   biosphere) :
    ei_reg = bd.Database(ei_name)
    bio = bd.Database(biosphere)

    if database_name not in bd.databases :
        print(f"{database_name} does not exist.")
        db = bd.Database(database_name)
        db.register()
        dfs, _, _ = calculate_processingsequence(eff, Li_conc, op_location, abbrev_loc)

        # Required activities and flows
        elec_search = find_activity_by_name_and_location("market for electricity, high voltage", ei_name, country_location)
        wastewater_search = find_activity_by_name_and_location("market for wastewater, average", ei_name, "RoW")
        waste_solid_search = find_activity_by_name_and_location("market for hazardous waste, for underground deposit",
                                                                ei_name, "RoW")
        heat_search = find_activity_by_name_and_location("heat production, natural gas, at industrial furnace >100kW",
                                                         ei_name, "RoW")
        steam_search = find_activity_by_name_and_location("market for steam, in chemical industry", ei_name, "RoW")

        #bio flows
        bio_search = find_bio_flow_by_name_and_category("Water, unspecified natural origin", bio,
                                                        ("natural resource", "in ground"))
        Li_search = find_bio_flow_by_name_and_category("Lithium", bio, ("natural resource", "in ground"))
        Na_search = find_bio_flow_by_name_and_category("Sodium", bio, ("water",))
        Cl_search = find_bio_flow_by_name_and_category("Chlorine", bio, ("water",))
        heat_waste_search = find_bio_flow_by_name_and_category("Heat, waste", bio, ("air",))

        chemical_map = {
            "HCl" : {
                "activity_name" : "market for hydrochloric acid, without water, in 30% solution state",
                "location" : "RoW"},
            "NaOH" : {
                "activity_name" : "sodium hydroxide to generic market for neutralising agent",
                "location" : "GLO"},
            "sodaash" : {
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

        for i, df in enumerate(dfs) :
            prev_df = dfs[i - 1] if i > 0 else None
            m_outputs = df[df['Variables'].str.contains('m_output_df_')]

            for _, m_output_row in m_outputs.iterrows() :
                activity_name = m_output_row["Variables"].split('m_output_')[1]
                new_act = db.new_activity(amount=1, code=activity_name, name=activity_name, unit="kilogram",
                                          location=country_location, type = "production")
                new_act.save()
                print(f"Created {activity_name}, {country_location} activity.")

                exchanges_df = df[df['Variables'].str.contains(activity_name)][1 :]

                for _, exchange_row in exchanges_df.iterrows() :
                    var = exchange_row['Variables']
                    if var == f"m_in_{activity_name}" :
                        # If you want to do something with the previous DataFrame
                        if prev_df is not None :
                            # Extract the activity name from prev_df, assuming the name can be derived similarly
                            prev_m_output_row = prev_df[prev_df['Variables'].str.contains('m_output_df_')].iloc[0]
                            prev_activity_name = prev_m_output_row["Variables"].split('m_output_')[1]
                            # Get the previously created activity from the database using the extracted name
                            prev_act = next((act for act in db if act['name'] == prev_activity_name), None)
                            # Create the exchange
                            new_act.new_exchange(input=prev_act.key, amount=exchange_row['per kg'], unit="kilogram",
                                                 type="technosphere").save()
                            print(f"Created exchange for {activity_name} activity.")
                        else :
                            pass

                    elif "m_Li" in var :
                        create_exchanges(new_act,
                                         [(Li_search.key, exchange_row['per kg'], "kilogram", "biosphere", None, None)])
                        print(f"Created {Li_search} exchange for {activity_name} activity.")
                    elif var == f"elec_{activity_name}" :
                        create_exchanges(new_act, [
                            (elec_search.key, exchange_row['per kg'], "kilowatt hour", "technosphere", None, None)])
                        print(f"Created {elec_search} exchange for {activity_name} activity.")
                    elif var.startswith(f"water_") :
                        act_search = next((act for act in db if act['name'] == f'Water_{abbrev_loc}'), None)
                        if not act_search :
                            water_act = db.new_activity(amount=1, code=f"Water_{abbrev_loc}",
                                                        name=f"Water_{abbrev_loc}", unit="kilogram",
                                                        location=country_location, type="production")
                            water_act.save()
                            exchanges = [
                                (elec_search.key, 0.007206, "kilowatt hour", "technosphere", country_location, None),
                                (wastewater_search.key, -0.00025, "cubic meter", "technosphere", "RoW", None),
                                (bio_search.key, 0.00025, "cubic meter", "biosphere", None,
                                 ("natural resource", "in ground"))
                                ]
                            create_exchanges(water_act, exchanges)
                            print(f"Created Water_{abbrev_loc} activity.")
                        else :
                            create_exchanges(new_act, [
                                (act_search.key, exchange_row['per kg'], "kilogram", "technosphere", None, None)])
                            print(f"Created {act_search} exchange for {activity_name} activity.")
                    elif var.startswith(f"E_") :
                        create_exchanges(new_act, [
                            (heat_search.key, exchange_row['per kg'], "megajoule", "technosphere", None, None)])
                        print(f"Created {heat_search} exchange for {activity_name} activity.")
                    elif "chemical_" in var :
                        for chem, details in chemical_map.items() :
                            if chem in var :
                                act_search = find_activity_by_name_and_location(details['activity_name'], ei_name,
                                                                                details['location'])
                                create_exchanges(new_act, [
                                    (act_search.key, exchange_row['per kg'], "kilogram", "technosphere",
                                     details['location'], None)])
                                print(f"Created {act_search} exchange for {activity_name} activity.")
                    elif var.startswith(f'steam') :
                        create_exchanges(new_act, [
                            (steam_search.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])
                        print(f"Created {steam_search} exchange for {activity_name} activity.")
                    elif var.startswith(f"waste_solid") :
                        create_exchanges(new_act, [
                            (waste_solid_search.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])
                        print(f"Created {waste_solid_search} exchange for {activity_name} activity.")
                    elif var.startswith(f'waste_liquid') :
                        create_exchanges(new_act, [
                            (wastewater_search.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])
                        print(f"Created {wastewater_search} exchange for {activity_name} activity.")
                    elif var.startswith(f'waste_heat') :
                        create_exchanges(new_act, [
                                         (heat_waste_search.key, exchange_row['per kg'], "megajoule", "biosphere", None, ('air',))])
                    elif var.startswith(f'waste_Na'):
                        create_exchanges(new_act, [
                            (Na_search.key, exchange_row['per kg'], "kilogram", "biosphere", None, ('water',))])
                    elif var.startswith(f'waste_Cl'):
                        create_exchanges(new_act, [
                            (Cl_search.key, exchange_row['per kg'], "kilogram", "biosphere", None, ('water',))])



    else :
        db = bd.Database(database_name)
        print(f"{database_name} already exists.")

    return db

#copy database so that at a later stage it can be changed
def copy_database(source_db_name, target_db_name):
    print(bd.databases)

    # Check if source database exists
    if source_db_name not in bd.databases:
        print(f"Source database {source_db_name} does not exist.")
        return None

    # Check if target database already exists
    if target_db_name in bd.databases:
        print(f"Target database {target_db_name} already exists.")
        return None

    # Now that we've checked both conditions, we can safely copy
    source_db = bd.Database(source_db_name)
    target_db = source_db.copy(target_db_name)

    return target_db

