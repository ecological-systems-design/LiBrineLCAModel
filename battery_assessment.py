import bw2data as bd
from pathlib import Path
from src.BW2_calculations.setting_up_bio_and_ei import import_biosphere,import_ecoinvent


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




