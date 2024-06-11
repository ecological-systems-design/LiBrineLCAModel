from pathlib import Path
import pandas as pd
import bw2calc as bc
import bw2data as bd
import os
from src.BW2_calculations.iterating_LCIs import change_exchanges_in_database
from src.BW2_calculations.impact_assessment import calculate_impacts
from src.BW2_calculations.setting_up_bio_and_ei import import_biosphere,import_ecoinvent
import datetime
from bw2io.utils import activity_hash
from copy import deepcopy
from src.BW2_calculations.impact_assessment import calculate_impacts





if __name__ == '__main__' :
    project = "battery_assessment_2"
    bd.projects.set_current(project)
    ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
    ei_name = f"ecoinvent 3.9.1 cutoff"
    biosphere = f"biosphere3"

    bio = import_biosphere(biosphere)
    ei = import_ecoinvent(ei_path,ei_name)

    act_nmc_battery = [act for act in ei if "battery production, Li-ion, NMC811, rechargeable, prismatic" in act['name']
                     and "CN" in act['location']][0]
    print(act_nmc_battery)

    act_lfp_battery = [act for act in ei if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                      and "CN" in act['location']][0]
    print(act_lfp_battery)

    country_list = ["CN", "US-WECC", "RER"]

    act_lfp_battery_copy = [act for act in ei if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                      and "CN" in act['location'] and "regionalized_battery" in act['code']]

    def change_regionalized_exchanges(act, country):
        exc_code_list = []

        for exc in act.exchanges() :
            exc_data = exc.as_dict()
            exc_code_list.append(exc_data['input'][1])

        act_list = []

        for exc_code in exc_code_list :
            act_check = [act for act in ei if exc_code in act['code'] and country in act['location']]
            if len(act_check) != 0 :
                act_list.append(act_check[0])

        if len(act_list) == 0:
            exc_to_be_substituted = [exc for exc in act.exchanges()][6]
            exc_to_be_substituted.delete()
            electricity_act = [act for act in ei if
                               "market for electricity, medium voltage" in act['name']
                               and country in act['location']][0]

            # Adding new electricity exchange to the activity
            act.new_exchange(input=electricity_act.key,amount=exc_to_be_substituted.amount,type='technosphere',
                             unit='kilowatt hour',
                             formula=1,location=country)
            act.save()

            print(act.as_dict())
            print(f'Added new electricity exchange to activity {act} for country {country}')
        else :
            print(f'Activity {act} already has regionalized exchanges for country {country}')

        return act

    act_list = []

    for country in country_list:
        print(country)
        act_lfp_battery_copy = [act for act in ei if
                                "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                                and country in act['location'] and f"regionalized_battery {country}" in act['code']]

        if len(act_lfp_battery_copy) == 0 :
            act_battery_copy = act_lfp_battery.copy()
            act_battery_copy['code'] = f"regionalized_battery {country}"
            act_battery_copy['location'] = country
            act_battery_copy.save()

            print(f'Created a copy of activity {act_lfp_battery} with code {act_battery_copy["code"]}')
        else :
            print(f'Activity {act_lfp_battery} already exists')

        act_lfp_battery_copy = [act for act in ei if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                          and country in act['location'] and f"regionalized_battery {country}" in act['code']][0]

        act_list.append(act_lfp_battery_copy)

        act_lfp_battery_copy = change_regionalized_exchanges(act_lfp_battery_copy, country)

    #calculate life cycle impacts for the regionalized battery production with ecoinvent data sets (Li2CO3)

    method_list = []
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
             and 'global warming potential' in str(m)][-20]

    method_list.append(method_cc)

    result_dict = { }



    for act in act_list:
        print(act)
        results = calculate_impacts(act, method_list)
        #add results to a dictionary
        result_dict[act] = results
        print(result_dict)
        print(f'Finished calculating impacts for activity {act}.')
        #save as csv file
    result_df = pd.DataFrame.from_dict(result_dict)
    result_df.to_csv(f'battery_impact_results.csv')













