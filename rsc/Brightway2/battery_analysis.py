import pandas as pd
import bw2calc as bc
import bw2data as bd
import os
from rsc.Brightway2.iterating_LCIs import change_exchanges_in_database
from rsc.Brightway2.impact_assessment import calculate_impacts
import datetime
from copy import deepcopy

#function to iterate over inventories of lithium and calculate impacts of batteries in ecoinvent
def calculate_impacts_of_battery(site_name, method, act_li):
    ei = bd.Database("ecoinvent 3.9.1 cutoff")
    site = bd.Database(site_name)

    #get the battery activity
    act_battery = [act for act in ei if "market for battery, Li-ion, NMC811, rechargeable, prismatic" in act['name']][0]
    act_battery_copy = deepcopy(act_battery.as_dict())
    act_battery_copy['code'] = "regionalized_battery"
    for exc in act_battery_copy.exchanges():
        new_exc = act_battery_copy(input = exc.input, amount =exc['amount'], type = exc['type'])
        #TODO work here!!!
        new_exc.save()

