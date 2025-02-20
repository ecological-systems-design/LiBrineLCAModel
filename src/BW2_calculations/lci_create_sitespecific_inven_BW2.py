import bw2data as bd
from copy import deepcopy

def creating_new_act(activities_to_copy, new_location, db) :
    for act_name, act_location, new_activity in activities_to_copy :
        new_act = [act for act in db if new_activity == act['name'] and new_location == act['location']]
        if len(new_act) == 0 :
            existing_act = [act for act in db if act_name == act['name'] and act_location == act['location']]
            assert len(existing_act) == 1
            existing_act = existing_act[0]
            # Copy existing activity, but change location
            new_act = existing_act.copy()
            new_act['name'] = new_activity
            new_act['location'] = new_location
            new_act['type'] = "process"
            new_act.save()
            #print(f"{new_act, new_act['type']} was successfully created.")
        else :
            print(f"{new_act} already exists")
    return db, new_act


def creating_supplychain(activities_to_copy, location,db) :
    for act_name, act_location, new_activity in activities_to_copy :
        new_act = [act for act in db if new_activity == act['name'] and location == act['location']]
        if len(new_act) == 0 :
            existing_act = [act for act in db if act_name == act['name'] and "WECC" == act['location']]
            print(existing_act)
            assert len(existing_act) == 1
            existing_act = existing_act[0]
            # Copy existing activity, but change location
            new_act = existing_act.copy()
            new_act['name'] = new_activity
            new_act['location'] = location
            new_act['type'] = "production"
            new_act.save()

            el_subst = [act for act in db if "deep well drilling, for deep geothermal power reg" in act['name']][0]
            exc = [exc for exc in el_subst.exchanges() if "electricity" in exc['name']][0]
            exc['amount'] = 0
            exc.save()
            el_subst.save()

            el_subst = [act for act in db if act['name'] == 'deep well drilling, for deep geothermal power'
                        and act['location'] == "WECC"]

            act_replace = [act for act in db if act['name'] == 'market for deep well, drilled, for geothermal ' \
                                                                   'power reg'][0]

            act_replace.new_exchange(input=el_subst[0].key, amount=1, unit='meter', type='technosphere').save()

            print(f"{act_replace, act_replace['type']} was successfully created.")

            for exchange in act_replace.exchanges() :
                exchange_type = exchange.get('type', 'Type not specified')
                print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

            act_replace = [act for act in db if act['name'] == "geothermal power plant construction reg"][0]

            el_subst = [act for act in db if act['name'] == 'deep well drilling, for deep geothermal power reg' and
                        act['location'] == location][0]

            [exc for exc in act_replace.exchanges()][1].delete()

            act_replace.new_exchange(input=el_subst.key, amount=32000, unit='meter', type='technosphere').save()
            print(f"{act_replace, act_replace['type']} was successfully created.")

            for exchange in act_replace.exchanges() :
                exchange_type = exchange.get('type', 'Type not specified')
                print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

            act_replace = [act for act in db if act['name'] == "market for geothermal power plant, 5.5MWel reg"][0]
            el_subst = [act for act in db if act['name'] == 'geothermal power plant construction reg'][0]

            for exc in act_replace.exchanges() :
                exc.delete()

            act_replace.new_exchange(input=el_subst.key, amount=1, unit='unit', type='technosphere').save()
            print(f"{act_replace, act_replace['type']} was successfully created.")

            for exchange in act_replace.exchanges() :
                exchange_type = exchange.get('type', 'Type not specified')
                print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

            act_replace = [act for act in db if act['name'] == "electricity production, deep geothermal reg"][0]
            el_subst = [act for act in db if act['name'] == 'market for geothermal power plant, 5.5MWel reg'][0]
            [exc for exc in act_replace.exchanges()][2].delete()

            act_replace.new_exchange(input=el_subst.key, amount=5.77700751010976e-10, unit='unit',
                                     type='technosphere').save()
            print(f"{act_replace, act_replace['type']} was successfully created and supply chain was created.")

            for exchange in act_replace.exchanges() :
                exchange_type = exchange.get('type', 'Type not specified')
                print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

            print(f"{new_act, new_act['type']} was successfully created.")

            for exchange in new_act.exchanges() :
                exchange_type = exchange.get('type', 'Type not specified')
                print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)
        else :
            print(f"{new_act} already exists")
    return db


def changing_electricity(act_list_f, db) :
    el_subst = [act for act in db if act['name'] == 'electricity production, deep geothermal reg']

    for act in act_list_f :
        for exc in act.exchanges() :
            name = exc.input['name']
            if name == 'electricity production, deep geothermal reg' :

                print('Already present')
                pass
            elif name == "electricity production, deep geothermal" :
                exc['name'] = el_subst[0]['name']
                exc['input'] = el_subst[0].key
                exc['type'] = "technosphere"
                exc.save()
                act.save()

                print('Adapted')
            else :
                pass


def changing_heat(act_f, db) :
    el_subst = [act for act in db if act['name'] == 'electricity production, deep geothermal reg'][0]
    print(el_subst['name'])
    for exc in act_f.exchanges() :
        name = exc.input['name']
        if name != el_subst["name"] :
            exc = [exc for exc in act_f.exchanges()][1]
            exc.delete()
            act_f.new_exchange(input=el_subst.key, amount=exc.amount, unit='unit', type='technosphere').save()
        else :
            pass


def changing_water_electricity(act_f, db) :
    exc = [exc for exc in act_f.exchanges()][1]
    exc.delete()
    el_subst = [act for act in db if act['name'] == 'electricity production, deep geothermal reg'][0]
    act_f.new_exchange(input=el_subst.key, amount=exc.amount, unit='unit', type='technosphere').save()


def wastewater(act_f, site_location, db) :
    for activity, location in act_f :
        # Check if the activity has already been treated
        act_new = [act for act in db if act['name'] == activity and act['location'] == location][0]
        if act_new.get('wastewater_treated') :
            continue  # Skip this activity if it was already treated

        el_subst = [act for act in db if "treatment of wastewater, average, wastewater treatment"
                    in act['name'] and site_location in act['location']][0]
        exc = [exc for exc in act_new.exchanges()][3]
        exc.delete()
        act_new.new_exchange(input=el_subst.key, amount=exc.amount, unit='unit', type='technosphere').save()

        # Set the wastewater_treated flag
        act_new['wastewater_treated'] = True
        act_new.save()
    return db


def chinese_coal(act_f, db) :
    for activity, location in act_f :
        act = [act for act in db if act['name'] == activity and act['location'] == location][0]
        if act.get('coal_adapted') :
            continue  # Skip this activity if it was already adapted

        [exc for exc in act.exchanges()][5].delete()
        el_subst = [act for act in db if act['name'] == 'market group for electricity, high voltage'
                    and act['location'] == 'CN'][0]
        act.new_exchange(input=el_subst.key, amount=0.0242, unit='kilowatt hour', type='technosphere').save()
        act.save()

        # Set the coal_adapted flag
        act['coal_adapted'] = True
        #print(f'Adapted {act, act["type"]}')
    return db


def create_fu(activity_list, site_name, db_name, site_location) :
    """
    Create a functional unit based on the given parameters.

    :param activity_list: A list of activities with their details
    :param db: The main database
    :param site_name: Site name to call the database
    :param site_location: The location of the site
    :return: Updated main database and site-specific database
    """
    site_db = bd.Database(site_name)
    db = bd.Database(db_name)

    lithium_carb = [act for act in site_db if act['name'] == "Geothermal Li" and act['location'] == site_location]

    if len(lithium_carb) == 0:
        lithium_carb = site_db.new_activity(amount=1, code="Geothermal Li", name="Geothermal Li", unit="kilogram",
                                            location=site_location, type="process")
        lithium_carb.save()
        lithium_carb.new_exchange(input=lithium_carb.key, amount=1, unit="kilogram",
                                                 type="production").save()
        lithium_carb.save()

        for activity, location, unit, act_db in activity_list :
            if activity == "df_rotary_dryer" :
                act = [act for act in site_db if act['name'] == activity and act['location'] == location][0]
                lithium_carb.new_exchange(amount=1, input=act, unit=unit, type="technosphere").save()
            elif activity == "deep well drilling, for deep geothermal power reg" :
                act = [act for act in db if act['name'] == activity and act['location'] == location][0]
                lithium_carb.new_exchange(amount=1, input=act, unit=unit, type="technosphere").save()
            else :
                print(f"Activity {activity} at {location} not found in {act_db}")

        lithium_carb.save()
        print(f"{lithium_carb} was successfully created.")
    else :
        print("'Geothermal Li' activity already exists.")

    return site_db

def adaptions_deposit_type(deposit_type, country_location, site_location, ei_name, site_name):

    db = bd.Database(ei_name)
    site_db = bd.Database(site_name)


    activity_list = [('heat production, natural gas, at industrial furnace >100kW', "RoW",
                           "heat production, natural gas, at industrial furnace >100kW"),
                     ("market for wastewater, average", "RoW",
                           "market for wastewater, average"),
                     ("treatment of wastewater, average, wastewater treatment", "RoW",
                           "treatment of wastewater, average, wastewater treatment"),
                     ("machine operation, diesel, >= 74.57 kW, high load factor", "GLO",
                           "machine operation, diesel, >= 74.57 kW, high load factor")]

    db, _ = creating_new_act(activity_list, site_location, db)

    act = [('hard coal mine operation and hard coal preparation', "CN")]
    db = chinese_coal(act, db)

    act = [('market for wastewater, average', site_location)]
    db = wastewater(act, site_location, db)

    if deposit_type == "geothermal" :
        activity_list = [("electricity production, deep geothermal", country_location,
                               "electricity production, deep geothermal" + " reg"),
                         ("market for geothermal power plant, 5.5MWel", "GLO",
                               "market for geothermal power plant, 5.5MWel" + " reg"),
                         ("geothermal power plant construction", "RoW",
                               "geothermal power plant construction" + " reg"),
                         ("market for deep well, drilled, for geothermal power", "GLO",
                               "market for deep well, drilled, for geothermal power" + " reg")]

        db, _ = creating_new_act(activity_list, country_location, db)


        activity_list = [('deep well drilling, for deep geothermal power', country_location,
                               "deep well drilling, for deep geothermal power" + " reg")]

        db = creating_supplychain(activity_list, country_location, db)

        activity_list = [
            ('df_rotary_dryer', site_location, 'kilogram', site_name),
            ('deep well drilling, for deep geothermal power reg', country_location, 'meter', ei_name)
            ]

        site_db = create_fu(activity_list, site_name, ei_name, site_location)



    else:
        pass

    return db, site_db


regionalized_activities = [('heat production, natural gas, at industrial furnace >100kW', "RoW"),
                     ("market for wastewater, average", "RoW"),
                     ("machine operation, diesel, >= 74.57 kW, high load factor", "GLO")]

def regionalize_activities(ei_name, site_name, site_location, regionalized_activities):

    regionalized_activity_names = [name for name, location in regionalized_activities]

    ei_reg = bd.Database(ei_name)
    site_db = bd.Database(site_name)

    act_list = [act for act in site_db]

    for act in act_list :
        #print(act)
        exc_list = [exc for exc in act.exchanges()]
        #print(exc_list)
        for exc in act.technosphere() :
            #print(exc, exc.input['name'])
            exc_name = exc.input['name']

            # Check if exc_name is in the list of regionalized activity names
            if exc_name in regionalized_activity_names :
                # Find the location associated with exc_name in regionalized_activities
                regional_location = next(loc for name, loc in regionalized_activities if name == exc_name)

                # If the activity's location in regionalized_activities is 'RoW' or 'GLO',
                # it means it's not specific and can be substituted with site_location
                if regional_location in ('RoW', 'GLO') :
                    # Fetch the regional equivalent activity
                    act_subst = next(
                        (act for act in ei_reg if act['name'] == exc_name and act['location'] == site_location), None)
                    # If an equivalent activity is found and its location is different, replace the exchange
                    if act_subst['location'] != regional_location :
                        exc['name'] = act_subst['name']
                        exc['input'] = act_subst.key
                        exc.save()
                        act.save()
                        #print(f"Regionalized technosphere exchange in {act['name']} at {site_location}")
                    else :
                        print(
                            f"Regionalized technosphere exchange already present for {act['name']} at {site_location}")
            else :
                print(f"No regionalization performed for {exc_name}")

    # Loop through all activities in the database
    # for activity in site_db :
    #     print("Activity:", activity, activity['type'])
    #     # Loop through all exchanges for the current activity
    #     for exchange in activity.exchanges() :
    #         exchange_type = exchange.get('type', 'Type not specified')
    #         print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)

    return ei_reg, site_db

def change_energy_provision(ei_name, copy_db_name, country, abbrev_loc):
    copy_db = bd.Database(copy_db_name)
    ei_reg = bd.Database(ei_name)

    # if abbrev_loc == "Ola":
    #     electricity_list = "heat and power co-generation, natural gas, 1MW electrical, lean burn"
    #     heat_list = "heat and power co-generation, natural gas, 1MW electrical, lean burn"
    if abbrev_loc == "Chaer" or abbrev_loc == "Yilip":
        electricity_list = "electricity, high voltage, production mix"
        heat_list = "heat production, natural gas, at industrial furnace >100kW"
    else:
        electricity_list = "market for electricity, high voltage"
        heat_list = "heat production, natural gas, at industrial furnace >100kW"

    if country == "BO" or country == "CL":
        country = "AR"

    if country == "CN-NWG":
        country = "CN-QH"

    photovoltaic_act = [act for act in ei_reg if act['name'] == "electricity production, photovoltaic, 570kWp open ground installation, multi-Si" and
                        act['location'] == country][0]

    cu_plate_act = [act for act in ei_reg if act['name'] == "operation, solar collector system, Cu flat plate collector, multiple dwelling, for hot water"
                    and act['location'] == "RoW"][0]

    act_list = [act for act in copy_db]

    for act in act_list :
        for exc in act.exchanges():
            name = exc.input['name']
            if electricity_list in name:
                exc['name'] = photovoltaic_act['name']
                exc['input'] = photovoltaic_act.key
                exc['type'] = "technosphere"
                exc.save()
                act.save()
                print('Electricity act was adapted in new database')

            elif heat_list in name:
                exc['name'] = cu_plate_act['name']
                exc['input'] = cu_plate_act.key
                exc['type'] = "technosphere"
                exc.save()
                act.save()
                print('Heat act was adapted in new database')

            else:
                print('No need to adapt activity')