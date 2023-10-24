
from rsc.lithium_production.licarbonate_processes import *
import pandas as pd
import os

if not os.path.exists("../inventories") :
    os.mkdir("../inventories")


def inventories(Li_conc, Li_conc_steps, max_eff, min_eff, eff_steps, max_number_boreholes, borehole_depth, op_location) :
    overall_eff = []
    while max_eff >= min_eff :
        overall_eff.append(max_eff)
        max_eff = max_eff - eff_steps

    Li_conc_all = []
    while Li_conc > 0 :
        Li_conc_all.append(Li_conc)
        Li_conc = Li_conc - Li_conc_steps


    drilling_scenarios = []

    if max_number_boreholes > 0 :
        while max_number_boreholes > 0 :
            drilling_scenarios.append(max_number_boreholes)
            max_number_boreholes = max_number_boreholes - 1
    else:
        drilling_scenarios = [0]

    ini_data = extract_data(op_location, abbrev_loc, Li_conc=Li_conc)

    prod = ini_data[abbrev_loc]["production"]  # Production of lithium carbonate [kg/yr]
    op_days = ini_data[abbrev_loc]["operation_days"]  # Operational days per year
    life = ini_data[abbrev_loc]["lifetime"]  # Expected time of mining activity [yr]
    v_pumpbrs = ini_data[abbrev_loc]["Brine_vol"]  # Brine pumped to the surface [L/s]
    v_pumpfrw = ini_data[abbrev_loc]["Freshwater_vol"]  # Fresh water pumped to the surface at evaporation ponds [L/s]
    eff = ini_data[abbrev_loc]["Li_efficiency"]  # Overall Li efficiency
    elev = ini_data[abbrev_loc]["elevation"]  # Elevation of mine site
    boil_point = ini_data[abbrev_loc]["boilingpoint_process"]  # Boiling point at processing plant [°C]
    T_out = ini_data[abbrev_loc]["annual_airtemp"]  # Annual air temperature [°C]
    Dens_ini = ini_data[abbrev_loc]["density_brine"]  # Density of initial brine [g/cm3]

    vec_end = ini_data[abbrev_loc]['vec_end']
    Li_conc = vec_end[0]

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
            df_list, summary_df, summary_tot_df = calculate_processingsequence(eff=eff, Li_conc=Li_c,
                                                                               location=op_location,
                                                                               abbrev_loc=abbrev_loc)
            energy.append(summary_tot_df['Energy_sum per output'].iloc[0])
            deion_water.append(summary_tot_df['Water_sum per output'].iloc[0])
            electricity.append(summary_tot_df['Electricity_sum per output'].iloc[0])

            energy_tot = energy_tot + energy
            deion_water_tot = deion_water_tot + deion_water
            electricity_tot = electricity_tot + electricity
            production_tot = production_tot + production

            df = df + df_list
            drilling_per_year.append(drill)

    data = {
        'Li' : pd.Series(list_Li_c, dtype='float64'),
        'eff' : pd.Series(list_eff, dtype='float64'),
        'sum impurities' : pd.Series(list_impurities_c, dtype='float64'),
        'Fe' : pd.Series(list_Fe_c, dtype='float64'),
        'Mn' : pd.Series(list_Mn_c, dtype='float64'),
        'Zn' : pd.Series(list_Zn_c, dtype='float64'),
        'Si' : pd.Series(list_Si_c, dtype='float64'),
        'Energy': pd.Series(energy_tot, dtype='float64'),
        'Water': pd.Series(deion_water_tot, dtype='float64'),
        'Electricity': pd.Series(electricity_tot, dtype='float64'),
        }


    demand_all = pd.DataFrame(data)
    print(demand_all)
    return demand_all, df


def best_case_steam(df_in) :
    iterator = list(range(int(len(df_in) / 17)))
    for j in range(len(iterator)) :
        df_in[j * 17 :(j + 1) * 17][7]['per kg'][3] = 0
    return df_in


