import bw2data as bd
import bw2io as bi
import bw2calc as bc
from copy import deepcopy
import pandas as pd
from openpyxl import load_workbook
import numpy as np
from pathlib import Path
from bw2io.utils import activity_hash
import bw2analyzer as bwa
import tabulate


def import_PM(ei, bio_f) :
    m = [m for m in bd.methods if "PM regionalized" in str(m)]
    if len(m) == 0 :
        particulates = [act for act in bio_f if 'particulate' in act['name'].lower() or 'sulfur dioxide' in act[
            'name'].lower() or 'nitrogen oxides' in act['name'].lower() or 'ammonia' in act['name'].lower()]
        bio_acts = particulates

        ei_loc_list = []
        for act in ei :
            if act.get('location') not in ei_loc_list :
                ei_loc_list.append(act.get('location'))

        new_bio_name = "biosphere PM regionalized"

        biosphere_data = {}
        for bio_act in bio_acts :
            for ei_loc in ei_loc_list :
                bio_act_data = deepcopy(bio_act.as_dict())
                bio_act_data['location'] = ei_loc  # Add location
                bio_act_data.pop('database')  # Remove database key
                dbname_code = (new_bio_name, activity_hash(bio_act_data))
                biosphere_data[dbname_code] = bio_act_data

        if new_bio_name in bd.databases :
            print(f"{new_bio_name} database already present!!! No import is needed")
        else :
            new_bio_db = bd.Database(new_bio_name)
            new_bio_db.write(biosphere_data)
            print(f"{new_bio_name} was created.")

        new_bio_db = bd.Database(new_bio_name)

        cf_pm1 = pd.read_csv(r"C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\CF_results_alternative_lithium_ecoinvent_regions_2022-02-14.csv", delimiter=';')
        cf_pm2_ada = pd.read_csv(r"C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\CF_PM_Geothermal.csv", delimiter=';')

        flows_list = []
        for flow in new_bio_db :
            for i in range(len(cf_pm1['Substance'])) :
                if str(cf_pm1['categories'][i]) in str(flow['categories']) and str(flow['name']) == str(
                        cf_pm1['Substance'][i]) and flow['location'] == cf_pm1['location'][i] :
                    flows_list.append([flow.key, cf_pm1['CF_DALY_per_kg'][i]])
            for i in range(len(cf_pm2_ada['Substance'])) :
                if str(flow['name']) == str(cf_pm2_ada['Substance'][i]) and \
                        flow['location'] == cf_pm2_ada['location'][i] and \
                        str(flow['categories']) in str(cf_pm2_ada['categories'][i]) :
                    flows_list.append([flow.key, cf_pm2_ada['CF_DALY_per_kg'][i]])

        # Write new BW method
        aware_tuple = ('PM regionalized', 'Annual', 'All')
        aware_method = bd.Method(aware_tuple)
        # new_lcia_method.deregister()  # To delete a method
        data = {
            'unit' : 'DALY',
            'num_cfs' : len(flows_list),
            'description' : 'xyz',
            }

        aware_method.validate(flows_list)
        aware_method.register()
        aware_method.write(flows_list)

        act_contain_water_list = []
        for act in ei :
            for exc in act.exchanges() :
                if exc.input in bio_acts :
                    act_contain_water_list.append(act)

        for act in act_contain_water_list :
            for exc in act.exchanges() :
                if exc.input in bio_acts :
                    flag_replaced = exc.get("replaced with regionalized", False)

                    if not flag_replaced :
                        # Copy data of the existing biosphere activity
                        data = deepcopy(exc.as_dict())
                        data.pop('flow')
                        # Find regionalized biosphere activity from the new biosphere database
                        bio_act_regionalized = [
                            bio_act for bio_act in new_bio_db if bio_act['name'] == exc.input['name']
                                                                 and bio_act['categories'] == exc.input['categories']
                                                                 and bio_act['location'] == act['location']
                            ]
                        assert len(bio_act_regionalized) == 1
                        bio_act_regionalized = bio_act_regionalized[0]
                        # Create new exchange that has all the data from the previous one, except for the input activity
                        # that is now from the new biosphere database
                        data['input'] = (bio_act_regionalized['database'], bio_act_regionalized['code'])
                        act.new_exchange(**data).save()
                        # Set the previous exchange amount to 0, we don't need None location anymore
                        exc['amount'] = 0  # exc.delete()?
                        # Mark that the exchange has been replaced
                        exc['replaced with regionalized'] = True
                        exc.save()
        print('PM is imported.')
        pass

    else :
        print("PM already exists as a method.")
        pass

    return None
