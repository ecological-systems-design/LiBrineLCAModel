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



def import_aware(ei, bio_f,site_name, site_db):
    if "AWARE regionalized" not in str(bd.methods) :
        plant_classi = ('EcoSpold01Categories', 'agricultural production/plant production')
        bio_acts = [act for act in bio_f if "water" in act['name'].lower() and
                    ('air' in act['categories'] or 'in air' in act['categories'])]
        ei_loc_list = []
        for act in ei :
            if act.get('location') not in ei_loc_list :
                ei_loc_list.append(act.get('location'))

        ei_loc_list.append(site_name)

        new_bio_name = "biosphere water regionalized"

        # combine locations with original water biosphere flows
        biosphere_data = {}
        for bio_act in bio_acts :
            for ei_loc in ei_loc_list :
                bio_act_data = deepcopy(bio_act.as_dict())
                bio_act_data['location'] = ei_loc  # Add location
                bio_act_data.pop('database')  # Remove database key
                dbname_code = (new_bio_name, activity_hash(bio_act_data))
                biosphere_data[dbname_code] = bio_act_data
        for bio_act in bio_acts :
            for ei_loc in ei_loc_list :
                bio_act_data = deepcopy(bio_act.as_dict())
                bio_act_data['location'] = ei_loc  # Add location
                bio_act_data.pop('database')  # Remove database key
                bio_act_data['name'] += ', irrigation'
                dbname_code = (new_bio_name, activity_hash(bio_act_data))
                biosphere_data[dbname_code] = bio_act_data

        if new_bio_name in bd.databases :
            print(f"{new_bio_name} database already present!!! No import is needed")
        else :
            new_bio_db = bd.Database(new_bio_name)
            new_bio_db.write(biosphere_data)
            print(f"{new_bio_name} was created.")

        new_bio_db = bd.Database(new_bio_name)

        cf_aware = pd.read_excel(r"data/AWARE_country_regions_Corrected_online_20230113-1.xlsx", engine='openpyxl',
                                 sheet_name='AWARE-annual')
        df_country = pd.read_excel(r"data/Country.xlsx", engine='openpyxl', sheet_name='Sheet1')
        df_country.loc[df_country.Country == "Namibia", "ISO2"] = "NA"

        flows_list = []
        unlinked_loc = []

        for flow in new_bio_db :
            loc_ei = flow.get('location')
            if '-' in loc_ei :
                loc_ei = loc_ei.split('-')[0]
            try :
                loc_aware = df_country.loc[df_country.ISO2 == loc_ei, "AWARE"].iloc[0]
                if 'irrigation' in flow.get('name') :
                    aware_score = cf_aware.loc[cf_aware.Country == loc_aware, "Agg_CF_irri"].iloc[0]
                else :
                    aware_score = cf_aware.loc[cf_aware.Country == loc_aware, "Agg_CF_non_irri"].iloc[0]
                flows_list.append([flow.key, aware_score])
            except :
                try :  # manual match
                    if 'irrigation' in flow.get('name') :
                        aware_score = cf_aware.loc[cf_aware.Ecoinvent_match == flow.get('location'), "Agg_CF_irri"].iloc[0]
                    else :
                        aware_score = \
                        cf_aware.loc[cf_aware.Ecoinvent_match == flow.get('location'), "Agg_CF_non_irri"].iloc[0]
                    flows_list.append([flow.key, aware_score])
                except :
                    if flow.get('location') not in unlinked_loc :
                        unlinked_loc.append(flow.get('location'))

        # Write new BW method
        aware_tuple = ('AWARE regionalized', 'Annual', 'All')
        aware_method = bd.Method(aware_tuple)
        # new_lcia_method.deregister()  # To delete a method
        data = {
            'unit' : 'm3 world',
            'num_cfs' : len(flows_list),
            'description' : 'xyz',
        }
        # aware_method.deregister()
        aware_method.validate(flows_list)
        aware_method.register()
        aware_method.write(flows_list)

        act_contain_water_list = []
        for act in ei :
            for exc in act.exchanges() :
                if exc.input in bio_acts :
                    act_contain_water_list.append(act)

        for act in site_db :
            for exc in act.exchanges() :
                if exc.input in bio_acts :
                    act_contain_water_list.append(act)

        print(f"Number of activities containing water: {len(act_contain_water_list), act_contain_water_list}")

        agri_act_list = []
        for x in act_contain_water_list :
            for i in x.get('classifications') :
                if i[0] == 'ISIC rev.4 ecoinvent' :
                    if (
                            ('011' in i[1] or '012' in i[1])
                            and '201' not in i[1]
                            and '301' not in i[1]
                    ) :
                        if i[1] not in agri_act_list :
                            agri_act_list.append(i[1])

        for act in act_contain_water_list :
            # check if act is agricultural event
            agri_yes_no = 0
            for classi in act.get('classifications') :
                if classi[1] in agri_act_list :
                    agri_yes_no += 1
                elif classi[1] == 'agricultural production/plant production' :
                    agri_yes_no += 1
            for exc in act.exchanges() :
                if exc.input in bio_acts :
                    flag_replaced = exc.get("replaced with regionalized", False)

                    if not flag_replaced :
                        # Copy data of the existing biosphere activity
                        data = deepcopy(exc.as_dict())
                        print(data)
                        print(exc.input['name'], act['name'])
                        data.pop('flow')
                        # Find regionalized biosphere activity from the new biosphere database
                        if agri_yes_no >= 1 :
                            exc_name = exc.input['name'] + ', irrigation'
                            bio_act_regionalized = [
                                bio_act for bio_act in new_bio_db if bio_act['name'] == exc_name
                                                                     and bio_act['categories'] == exc.input['categories']
                                                                     and bio_act['location'] == act['location']
                            ]
                            data['name'] += ', irrigation'
                        else :
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

        print(f'AWARE is imported.')
        pass
    else:
        print(f"AWARE already exists as a method.")
        pass


