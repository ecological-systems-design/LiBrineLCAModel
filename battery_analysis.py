from pathlib import Path
import pandas as pd
import bw2calc as bc
import bw2data as bd
import os
from rsc.Brightway2.iterating_LCIs import change_exchanges_in_database
from rsc.Brightway2.impact_assessment import calculate_impacts
from rsc.Brightway2.setting_up_bio_and_ei import import_biosphere,import_ecoinvent
import datetime
from bw2io.utils import activity_hash
from copy import deepcopy





if __name__ == '__main__' :
    project = "battery_assessment_1"
    bd.projects.set_current(project)
    ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
    ei_name = f"ecoinvent 3.9.1 cutoff"
    biosphere = f"biosphere3"

    bio = import_biosphere(biosphere)
    ei = import_ecoinvent(ei_path,ei_name)


    batt_act = [act for act in ei if "market for battery, Li-ion, NMC811, rechargeable, prismatic" in act['name']][0]

    print(batt_act)

    act_nmc_battery = [act for act in ei if "battery production, Li-ion, NMC811, rechargeable, prismatic" in act['name']
                     and "CN" in act['location']][0]
    print(act_nmc_battery)

    act_lfp_battery = [act for act in ei if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                      and "CN" in act['location']][0]
    print(act_lfp_battery)

    act_lfp_battery_copy = [act for act in ei if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                      and "CN" in act['location'] and "regionalized_battery" in act['code']]

    if len(act_lfp_battery_copy) == 0 :
        act_battery_copy = act_lfp_battery.copy()
        act_battery_copy['code'] = "regionalized_battery"
        act_battery_copy.save()

        print(f'Creating a copy of activity {act_lfp_battery} with code {act_battery_copy["code"]}')
    else :
        print(f'Activity {act_lfp_battery} already exists')

    act_lfp_battery_copy = [act for act in ei if "battery production, Li-ion, LFP, rechargeable, prismatic" in act['name']
                      and "CN" in act['location'] and "regionalized_battery" in act['code']][0]

    for exc in act_battery_copy.exchanges():
        print(exc)


