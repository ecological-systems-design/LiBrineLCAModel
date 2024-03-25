import bw2data as bd
#from rsc.lithium_production.licarbonate_processes import calculate_processingsequence



# Define your mapping for activities outside the function
def create_activity_map(country_location, abbrev_loc):
    if abbrev_loc == "Ola":
        electricity_list = ("heat and power co-generation, natural gas, 1MW electrical, lean burn", "RoW")
        heat_list = ("heat and power co-generation, natural gas, 1MW electrical, lean burn", "RoW")
    elif abbrev_loc == "Chaer":
        electricity_list = ("electricity, high voltage, production mix", country_location)
        heat_list = ("heat production, natural gas, at industrial furnace >100kW", "RoW")
    else:
        electricity_list = ("market for electricity, high voltage", country_location)
        heat_list = ("heat production, natural gas, at industrial furnace >100kW", "RoW")

    print(electricity_list)
    print(heat_list)

    activity_map = {
        'elec_high_voltage': electricity_list,
        'wastewater_average': ("market for wastewater, average", "RoW"),
        'waste_hazardous_underground': ("market for hazardous waste, for underground deposit", "RoW"),
        'waste_nonhazardous_landfill': ("treatment of waste gypsum, inert material landfill", "RoW"),
        'heat_industrial_gas': heat_list,
        'steam_chemical_industry': ("market for steam, in chemical industry", "RoW"),
        'diesel_machine_high_load': ("machine operation, diesel, >= 74.57 kW, high load factor", "GLO"),
        'salt_tailing_landfill': ("treatment of salt tailing from potash mine, residual material landfill", "RoW"),
        'transport_freight_lorry_euro3': ("transport, freight, lorry >32 metric ton, EURO3", "RoW"),
        'spent_solvent_treatment': ("treatment of spent solvent mixture, hazardous waste incineration", "RoW"),
    }

    return activity_map


def create_bio_flow_map():
    bio_flow_map = {
        'water_unspecified': ("Water, unspecified natural origin", ("natural resource", "in ground")),
        'water_evaporated': ("Water", ("air",)),
        'lithium': ("Lithium", ("natural resource", "in ground")),
        'sodium': ("Sodium", ("water",)),
        'chlorine': ("Chlorine", ("water",)),
        'heat_waste': ("Heat, waste", ("air",)),
        'occupation_extraction_site': ("Occupation, mineral extraction site", ("natural resource", "land")),
        'transformation_unknown': ("Transformation, from unknown", ("natural resource", "land")),
        'transformation_to_extraction_site': ("Transformation, to mineral extraction site", ("natural resource", "land")),
    }
    return bio_flow_map

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
        "location" : "RoW"},
    "organicsolvent" : {
        "activity_name" : "market for solvent, organic",
        "location" : "GLO"},
    "calciumchloride": {
        "activity_name": "market for calcium chloride",
        "location": "RoW"},
    "sulfuricacid": {
        "activity_name": "market for sulfuric acid",
        "location": "RoW"}

    }

def find_activity_by_name_and_location(name, ei_name, location) :
    if ei_name not in bd.databases :
        raise ValueError(f"Database {ei_name} does not exist.")

    ei_reg = bd.Database(ei_name)
    return next((act for act in ei_reg if act['name'] == str(name) and act['location'] == location), None)


def find_bio_flow_by_name_and_category(name, database, categories) :
    bio_flow = next((bio_flow for bio_flow in database if bio_flow['name'] == str(name)
                     and bio_flow['categories'] == categories), None)
    return bio_flow

# Use the mapping within your function to retrieve and process the data
def search_activities_and_flows(ei_name, bio, activity_map, bio_flow_map):
    for key, (name, location) in activity_map.items():
        # Assuming find_activity_by_name_and_location is previously defined and takes name, ei_name, location
        activity_search = find_activity_by_name_and_location(name, ei_name, location)
        return activity_search

    for key, (name, categories) in bio_flow_map.items():
        # Assuming find_bio_flow_by_name_and_category is previously defined and takes name, bio, categories
        bio_search = find_bio_flow_by_name_and_category(name, bio, categories)
        return bio_search


def create_exchanges(activity, exchanges) :
    for key, amount, unit, type_, location, categories in exchanges :
        activity.new_exchange(input=key, amount=amount, unit=unit, type=type_,
                              location=location, categories=categories).save()
        print(f"Created exchange for {activity} activity.")


def create_database(database_name, country_location, eff, Li_conc, op_location, abbrev_loc, ei_name,
                   biosphere, dataframes_dict, chemical_map, deposit_type) :
    ei_reg = bd.Database(ei_name)
    bio = bd.Database(biosphere)

    if database_name not in bd.databases :
        print(f"{database_name} does not exist.")
        db = bd.Database(database_name)
        db.register()

        # Required activities and flows
        activity_map = create_activity_map(country_location, abbrev_loc)
        print(activity_map)
        bio_flow_map = create_bio_flow_map()

        activity_objects = {key : find_activity_by_name_and_location(name, ei_name, location)
                            for key, (name, location) in activity_map.items()}

        bio_flow_objects = {key : find_bio_flow_by_name_and_category(name, bio, categories)
                            for key, (name, categories) in bio_flow_map.items()}

        dfs = list(dataframes_dict.values())
        keys = list(dataframes_dict.keys())

        for i, (key, df) in enumerate(dataframes_dict.items()) :
            prev_df = dfs[i - 1] if i > 0 else None
            m_outputs = df[df['Variables'].str.contains('^m_output_df_', na=False)]

            for _, m_output_row in m_outputs.iterrows() :
                activity_name = m_output_row["Variables"].split('m_output_')[1]
                new_act = db.new_activity(amount=1, code=activity_name, name=activity_name, unit="kilogram",
                                          location=op_location, type="process")
                print(new_act)
                new_act['classifications'] = [('ISIC rev.4 ecoinvent', '0729')]
                new_act['flow'] = activity_name
                new_act.save()
                new_act.new_exchange(input=new_act.key, amount=1, unit="kilogram", type="production").save()

                print(f"Created {activity_name}, {op_location} activity.")

                exchanges_df = df[df['Variables'].str.contains(activity_name)][1 :]

                for _, exchange_row in exchanges_df.iterrows() :
                    var = exchange_row['Variables']
                    if var == f"m_in_{activity_name}" :
                        if prev_df is not None :
                            # Extract the activity name from prev_df, assuming the name can be derived similarly
                            prev_m_output_row = prev_df[prev_df['Variables'].str.contains('m_output')].iloc[0]
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
                        li_flow = bio_flow_objects['lithium']
                        create_exchanges(new_act,
                                         [(li_flow.key, exchange_row['per kg'], "kilogram", "biosphere", None, None)])
                        print(f"Created {li_flow} exchange for {activity_name} activity.")

                    elif var == f"elec_{activity_name}" :
                        elec_flow = activity_objects['elec_high_voltage']
                        create_exchanges(new_act, [
                            (elec_flow.key, exchange_row['per kg'], "kilowatt hour", "technosphere", country_location, None)])
                        print(f"Created {elec_flow} exchange for {activity_name} activity.")

                    elif var == f"water_{activity_name}" :
                        act_search = next((act for act in db if act['name'] == f'Water_{abbrev_loc}'), None)
                        print(act_search)

                        if not act_search :
                            water_act = db.new_activity(amount=1, code=f"Water_{abbrev_loc}",
                                                        name=f"Water_{abbrev_loc}", unit="kilogram",
                                                        location=op_location, type="process")
                            water_act['classifications'] = [('ISIC rev.4 ecoinvent', '0729')]
                            water_act['flow'] = f"Water_{abbrev_loc}"
                            water_act.save()
                            water_act.new_exchange(input=water_act.key, amount=1, unit="kilogram",
                                                   location = op_location, type="production").save()
                            water_act.save()
                            if deposit_type == "geothermal":
                                wastewater_flow = activity_objects['wastewater_average']
                                water_flow = bio_flow_objects['water_unspecified']
                                elec_flow = activity_objects['elec_high_voltage']
                                exchanges = [
                                    (elec_flow.key, 0.007206, "kilowatt hour", "technosphere", country_location, None),
                                    (wastewater_flow.key, 0.00025, "cubic meter", "technosphere", "RoW", None),
                                    (water_flow.key, 0.00025, "cubic meter", "biosphere", None,
                                     ("natural resource", "in ground"))
                                    ]
                                create_exchanges(water_act, exchanges)
                            elif deposit_type == "salar":
                                elec_flow = activity_objects['elec_high_voltage']
                                water_flow = bio_flow_objects['water_unspecified']
                                water_evaporated_flow = bio_flow_objects['water_evaporated']
                                exchanges = [
                                    (elec_flow.key, 0.007206, "kilowatt hour", "technosphere", country_location, None),
                                    (water_flow.key, 0.00125, "cubic meter", "biosphere", None,
                                     ("natural resource", "in ground")),
                                    (water_evaporated_flow.key, 0.00025, "cubic meter", "biosphere", None,
                                     ("air",))
                                    ]
                                create_exchanges(water_act, exchanges)


                            print(f"Created Water_{abbrev_loc} activity.")
                        else :
                            pass
                        act_search = next((act for act in db if act['name'] == f'Water_{abbrev_loc}'), None)
                        create_exchanges(new_act, [
                            (act_search.key, exchange_row['per kg'], "kilogram", "technosphere", None, None)])

                    elif var.startswith(f"E_") :
                        heat_flow = activity_objects['heat_industrial_gas']
                        create_exchanges(new_act, [
                            (heat_flow.key, exchange_row['per kg'], "megajoule", "technosphere", None, None)])

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
                        steam_flow = activity_objects['steam_chemical_industry']
                        create_exchanges(new_act, [
                            (steam_flow.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])

                    elif var.startswith(f"waste_salt") :
                        salt_flow = activity_objects['salt_tailing_landfill']
                        create_exchanges(new_act, [
                            (salt_flow.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])

                    elif var.startswith(f'waste_solid') :
                        if deposit_type == "geothermal":
                            waste_solid_flow = activity_objects['waste_hazardous_underground']
                            create_exchanges(new_act, [
                                (waste_solid_flow.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])
                        elif deposit_type == "salar":
                            waste_solid_flow = activity_objects['waste_nonhazardous_landfill']
                            create_exchanges(new_act, [
                                (waste_solid_flow.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])


                    elif var.startswith(f'waste_liquid') :
                        if deposit_type == "geothermal":
                            wastewater_flow = activity_objects['wastewater_average']
                            create_exchanges(new_act, [
                            (wastewater_flow.key, exchange_row['per kg']/1000, "cubic meter", "technosphere", "RoW", None)])
                        elif deposit_type == "salar":
                            act_search = next((act for act in db if act['name'] == f'waste_liquid_{abbrev_loc}'), None)

                            if not act_search :
                                act = db.new_activity(amount=1, code=f"waste_liquid_{abbrev_loc}",
                                                            name=f"waste_liquid_{abbrev_loc}", unit="cubic meter",
                                                            location=op_location, type="process")
                                act['classifications'] = [('ISIC rev.4 ecoinvent', '0729')]
                                act['flow'] = f"waste_liquid_{abbrev_loc}"
                                act.save()
                                act.new_exchange(input=act.key, amount=1, unit="cubic meter",
                                                       type="production").save()
                                act.save()
                                # adding relevant exchanges to new activity
                                water_evaporated_flow = bio_flow_objects['water_evaporated']
                                wastewater_flow = activity_objects['wastewater_average']
                                ratio_wastewater_evaporated = 0.1
                                create_exchanges(act, [
                                    (wastewater_flow.key, ratio_wastewater_evaporated * exchange_row['per kg']/1000,
                                     "cubic meter", "technosphere", "RoW", None),
                                    (water_evaporated_flow.key, (1-ratio_wastewater_evaporated) * exchange_row['per kg']/1000,
                                     "cubic meter", "biosphere", None, ('air',))
                                    ])
                                print(f"Created waste_liquid_{abbrev_loc} activity.")

                            else :
                                pass
                            act_search = next((act for act in db if act['name'] == f'waste_liquid_{abbrev_loc}'), None)
                            create_exchanges(new_act, [
                                (act_search.key, exchange_row['per kg']/1000, "cubic meter", "technosphere", None, None)])


                    elif var.startswith(f'waste_heat') :
                        waste_heat_flow = bio_flow_objects['heat_waste']
                        create_exchanges(new_act, [
                                         (waste_heat_flow.key, exchange_row['per kg'], "megajoule", "biosphere", None, ('air',))])

                    elif var.startswith(f'waste_Na'):
                        waste_Na_flow = bio_flow_objects['sodium']
                        create_exchanges(new_act, [
                            (waste_Na_flow.key, exchange_row['per kg'], "kilogram", "biosphere", None, ('water',))])

                    elif var.startswith(f'waste_Cl'):
                        waste_Cl_flow = bio_flow_objects['chlorine']
                        create_exchanges(new_act, [
                            (waste_Cl_flow.key, exchange_row['per kg'], "kilogram", "biosphere", None, ('water',))])

                    elif var.startswith(f'transport'):
                        transport_flow = activity_objects['transport_freight_lorry_euro3']
                        create_exchanges(new_act, [
                            (transport_flow.key, exchange_row['per kg'], "ton kilometer", "technosphere", "RoW", None)])

                    elif var.startswith(f'land_occupation'):
                        occupation_flow = bio_flow_objects['occupation_extraction_site']
                        create_exchanges(new_act, [
                            (occupation_flow.key, exchange_row['per kg'], "square meter-year", "biosphere", None, ('natural resource', 'land'))])

                    elif var.startswith(f'land_transform_unknown'):
                        transform_unknown_flow = bio_flow_objects['transformation_unknown']
                        create_exchanges(new_act, [
                            (transform_unknown_flow.key, exchange_row['per kg'], "square meter", "biosphere", None, ('natural resource', 'land'))])

                    elif var.startswith(f'land_transform_minesite'):
                        transform_minesite_flow = bio_flow_objects['transformation_to_extraction_site']
                        create_exchanges(new_act, [
                            (transform_minesite_flow.key, exchange_row['per kg'], "square meter", "biosphere", None, ('natural resource', 'land'))])

                    elif var.startswith(f'diesel_machine'):
                        diesel_flow = activity_objects['diesel_machine_high_load']
                        create_exchanges(new_act, [
                            (diesel_flow.key, exchange_row['per kg'], "kilogram", "technosphere", "GLO", None)])

                    elif var.startswith(f'waste_organicsolvent'):
                        waste_organic_flow = activity_objects['spent_solvent_treatment']
                        create_exchanges(new_act, [
                            (waste_organic_flow.key, exchange_row['per kg'], "kilogram", "technosphere", "RoW", None)])

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

