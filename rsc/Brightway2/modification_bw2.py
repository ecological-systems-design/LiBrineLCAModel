import bw2data as bd

location = 'US-WECC'
activity_to_copy = "electricity production, deep geothermal"
new_activity = activity_to_copy + "reg"
activities_to_copy = [(activity_to_copy, location, new_activity)]
ei_name = "ecoinvent 3.9.1 cutoff"
ei_reg = bd.Database(ei_name)
site_name = f"Salton_39"
site_location = site_name[:3]
water_name = f"Water_39"
water = bd.Database(water_name)
site = bd.Database(site_name)


def creating_new_act(activities_to_copy, location):
    for act_name, act_location, new_activity in activities_to_copy:
        new_act = [act for act in ei_reg if new_activity == act['name'] and location == act['location']]
        if len(new_act) == 0:
            existing_act = [act for act in ei_reg if act_name == act['name'] and act_location == act['location']]
            assert len(existing_act) == 1
            existing_act = existing_act[0]
            # Copy existing activity, but change location
            new_act = existing_act.copy()
            new_act['name'] = new_activity
            new_act['location'] = location
            new_act.save()
            print(f"{new_act} was successfully created.")
        else:
            print(f"{new_act} already exists")


def creating_supplychain(activities_to_copy, location):
    for act_name, act_location, new_activity in activities_to_copy:
        new_act = [act for act in ei_reg if new_activity == act['name'] and location == act['location']]
        if len(new_act) == 0:
            existing_act = [act for act in ei_reg if act_name == act['name'] and act_location == act['location']]
            assert len(existing_act) == 1
            existing_act = existing_act[0]
            # Copy existing activity, but change location
            new_act = existing_act.copy()
            new_act['name'] = new_activity
            new_act['location'] = location
            new_act.save()

            el_subst = [act for act in ei_reg if "deep well drilling, for deep geothermal power reg" in act['name']][0]
            exc = [exc for exc in el_subst.exchanges() if "electricity" in exc['name']][0]
            exc['amount'] = 0
            exc.save()
            el_subst.save()

            el_subst = [act for act in ei_reg if act['name'] == 'deep well drilling, for deep geothermal power'
                        and act['location'] == 'WECC']

            act_replace = [act for act in ei_reg if act['name'] == 'market for deep well, drilled, for geothermal ' \
                                                                   'power reg'][0]

            act_replace.new_exchange(input=el_subst[0].key, amount=1, unit='meter', type='technosphere').save()

            act_replace= [act for act in ei_reg if act['name'] == "geothermal power plant construction reg"][0]

            el_subst = [act for act in ei_reg if act['name'] == 'deep well drilling, for deep geothermal power reg' and
                        act['location'] == location][0]


            [exc for exc in act_replace.exchanges()][1].delete()

            act_replace.new_exchange(input=el_subst.key, amount=32000, unit='meter', type='technosphere').save()

            act_replace = [act for act in ei_reg if act['name'] == "market for geothermal power plant, 5.5MWel reg"][0]
            el_subst = [act for act in ei_reg if act['name'] == 'geothermal power plant construction reg'][0]

            for exc in act_replace.exchanges():
                exc.delete()

            act_replace.new_exchange(input=el_subst.key, amount=1, unit='unit', type='technosphere').save()

            act_replace = [act for act in ei_reg if act['name'] == "electricity production, deep geothermal reg"][0]
            el_subst = [act for act in ei_reg if act['name'] == 'market for geothermal power plant, 5.5MWel reg'][0]
            [exc for exc in act_replace.exchanges()][2].delete()

            act_replace.new_exchange(input=el_subst.key, amount=5.77700751010976e-10, unit='unit',
                                     type='technosphere').save()

            print(f"{new_act} was successfully created and supply chain was created.")
        else:
            print(f"{new_act} already exists")


def changing_electricity(act_list_f) :
    el_subst = [act for act in ei_reg if act['name'] == 'electricity production, deep geothermal reg']

    for act in act_list_f :
        for exc in act.exchanges() :
            name = exc.input['name']
            if name == 'electricity production, deep geothermal reg' :

                print('Already present')
                pass
            elif name == "electricity production, deep geothermal" :
                exc['name'] = el_subst[0]['name']
                exc['input'] = el_subst[0].key
                exc.save()
                act.save()

                print('Adapted')
            else :
                pass


def changing_heat(act_f):
    el_subst = [act for act in ei_reg if act['name'] == 'electricity production, deep geothermal reg'][0]
    print(el_subst['name'])
    for exc in act_f.exchanges() :
        name = exc.input['name']
        if name != el_subst["name"] :
            exc = [exc for exc in act_f.exchanges()][1]
            exc.delete()
            act_f.new_exchange(input=el_subst.key, amount=exc.amount, unit='unit', type='technosphere').save()
        else:
            pass


def changing_water_electricity(act_f):
    exc = [exc for exc in act_f.exchanges()][1]
    exc.delete()
    el_subst = [act for act in ei_reg if act['name'] == 'electricity production, deep geothermal reg'][0]
    act_f.new_exchange(input=el_subst.key, amount=exc.amount, unit='unit', type='technosphere').save()

def wastewater(act_f):
    el_subst = [act for act in ei_reg if "treatment of wastewater, average, wastewater treatment reg"
                in act['name'] and site_location in act['location']][0]
    exc = [exc for exc in act_f.exchanges()][3]
    exc.delete()
    act_f.new_exchange(input=el_subst.key, amount=exc.amount, unit='unit', type='technosphere').save()

def chinese_coal(act_f):
    [exc for exc in act_f.exchanges()][5].delete()
    el_subst = [act for act in ei_reg if act['name'] == 'market group for electricity, high voltage'
                and act['location'] == 'CN'][0]
    act_f.new_exchange(input=el_subst.key, amount=0.0242, unit='kilowatt hour', type='technosphere').save()

def create_new_act(act_f, location_f):
    lithium_carb = water.new_activity(amount=1, code="Geothermal Li", name="Geothermal Li", unit="kilogram",
                                      location=location)
    lithium_carb.save()
    drilling = [act for act in ei_reg if "deep well drilling, for deep geothermal power reg" in act['name']
                and "WECC" in act['location']][0]
    lithium_carb.new_exchange(amount=1, input=act_f, type="technosphere").save()
    lithium_carb.new_exchange(amount=3600, input=drilling, type="technosphere").save()
    lithium_carb.save()




