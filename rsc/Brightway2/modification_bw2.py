import bw2data as bd


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
            print(f"{new_act, new_act['type']} was successfully created.")
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
    for activity, location in act_f:
        el_subst = [act for act in db if "treatment of wastewater, average, wastewater treatment reg"
                    in act['name'] and site_location in act['location']][0]
        act_new = [act for act in db if act['name'] == activity and act['location'] == location][0]
        exc = [exc for exc in act_new.exchanges()][3]
        exc.delete()
        act_new.new_exchange(input=el_subst.key, amount=exc.amount, unit='unit', type='technosphere').save()
    return db

def chinese_coal(act_f,db) :
    for activity, location in act_f:
        act = [act for act in db if act['name'] == activity and act['location'] == location][0]
        [exc for exc in act.exchanges()][5].delete()
        el_subst = [act for act in db if act['name'] == 'market group for electricity, high voltage'
                    and act['location'] == 'CN'][0]
        act.new_exchange(input=el_subst.key, amount=0.0242, unit='kilowatt hour', type='technosphere').save()
        act.save()

        print(f'Adapted {act, act["type"]}')
        for exchange in act.exchanges() :
            exchange_type = exchange.get('type', 'Type not specified')
            print("\tExchange:", exchange.input, "->", exchange.amount, exchange.unit, exchange_type)
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
        print("Creating 'Geothermal Li' activity.")
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


#act = [act for act in act_db if act['name'] == activity and act['location'] == location][0]
def adaptions_deposit_type(deposit_type, country_location, site_location, ei_name, site_name):

    db = bd.Database(ei_name)
    site_db = bd.Database(site_name)


    activity_list = [('heat production, natural gas, at industrial furnace >100kW', "RoW",
                           "heat production, natural gas, at industrial furnace >100kW"),
                     ("market for wastewater, average", "RoW",
                           "market for wastewater, average" + " reg"),
                     ("treatment of wastewater, average, wastewater treatment", "RoW",
                           "treatment of wastewater, average, wastewater treatment" + " reg")]

    db, _ = creating_new_act(activity_list, site_location, db)

    act = [('hard coal mine operation and hard coal preparation', "CN")]
    db = chinese_coal(act, db)

    act = [('market for wastewater, average reg', site_location)]
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
            ('df_rotary_dryer', country_location, 'kilogram', site_name),
            ('deep well drilling, for deep geothermal power reg', country_location, 'meter', ei_name)
            ]

        site_db = create_fu(activity_list, site_name, ei_name, site_location)



    else:
        pass

    return db, site_db

