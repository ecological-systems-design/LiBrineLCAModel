
from rsc.lithium_production.processes import *
import pandas as pd
import os

if not os.path.exists("../../inventories") :
    os.mkdir("../../inventories")


def inventories(Li_conc, max_eff, min_eff, eff_steps, max_number_boreholes, borehole_depth) :
    overall_eff = []
    while max_eff >= min_eff :
        overall_eff.append(max_eff)
        max_eff = max_eff - eff_steps

    Li_conc_all = []
    while Li_conc > 0 :
        Li_conc_all.append(Li_conc)
        Li_conc = Li_conc - 0.001

    drilling_scenarios = []

    if max_number_boreholes > 0 :
        while max_number_boreholes > 0 :
            drilling_scenarios.append(max_number_boreholes)
            max_number_boreholes = max_number_boreholes - 1
    else:
        drilling_scenarios = [0]



    energy_tot = []
    deion_water_tot = []
    electricity_tot = []
    production_tot = []
    drilling_per_year = []

    df = []
    list_Li_c = []
    list_eff = []

    list_impurities_c = []
    list_Mn_c = []
    list_Fe_c = []
    list_Si_c = []
    list_Zn_c = []


    for drill in drilling_scenarios :
        for Li_c in Li_conc_all :
            list_eff.append(eff)
            list_Li_c.append(Li_c)
            list_impurities_c.append(vec_end[-5] + vec_end[-4] + vec_end[8] + vec_end[-3])
            list_Mn_c.append(vec_end[-5])
            list_Fe_c.append(vec_end[-4])
            list_Si_c.append(vec_end[8])
            list_Zn_c.append(vec_end[-3])
            deion_water = []
            energy = []
            electricity = []
            production = []
            df_list, summary_df, summary_tot_df = loop_functions(eff=eff, Li_conc = Li_c)
            df_inven = df_list
            energy_tot = energy_tot + energy
            deion_water_tot = deion_water_tot + deion_water
            electricity_tot = electricity_tot + electricity
            production_tot = production_tot + production

            df = df + df_inven
            drilling_per_year.append(drill)

    data = {
        'Li' : pd.Series(list_Li_c, dtype='float64'),
        'eff' : pd.Series(list_eff, dtype='float64'),
        'sum impurities' : pd.Series(list_impurities_c, dtype='float64'),
        'Fe' : pd.Series(list_Fe_c, dtype='float64'),
        'Mn' : pd.Series(list_Mn_c, dtype='float64'),
        'Zn' : pd.Series(list_Zn_c, dtype='float64'),
        'Si' : pd.Series(list_Si_c, dtype='float64'),
        'energy' : pd.Series(energy_tot, dtype='float64').sum(),
        'electricity' : pd.Series(electricity_tot, dtype='float64').sum(),
        'water' : pd.Series(deion_water_tot, dtype='float64').sum()
        }

    demand_all = pd.DataFrame(data)
    return demand_all, df


def best_case_steam(df_in) :
    iterator = list(range(int(len(df_in) / 17)))
    for j in range(len(iterator)) :
        df_in[j * 17 :(j + 1) * 17][7]['per kg'][3] = 0
    return df_in


