
# operational_and_environmental_constants.py


DEFAULT_CONSTANTS = {
    'H': 1.008,
    'Mg': 24.31,
    'B': 10.81,
    'S': 32.07,
    'Ca': 40.08,
    'Li': 6.94,
    'C': 12.011,
    'O': 15.999,
    'Na': 22.99,
    'Cl': 35.45,
    'K': 39.098,
    'Si': 28.085,
    'As': 74.922,
    'Mn': 54.938,
    'Fe': 55.845,
    'Zn': 65.38,
    'Ba': 137.33,
    'Sr': 87.62,
    'gravity_constant': 9.81,
    'hCC': 849,
    'hCH': 1996,
    'hCHH': 4190,
    'hCHH_bri': 3219.94,
    'hCLi': 1341,
    'heat_natgas': 40.4,
    'heat_propgas': 44.33,
    'latheat_H': 2257000,
    'dens_NaCl': 2160,
    'dens_Soda': 2540,
    'dens_CaCl': 2150,
    'dens_Licarb': 2100,
    'dens_H2O': 1000,
    'dens_pulp': 2 / 3 * 1000 + 1 / 3 * 2100,
    'dens_frw': 1100,
    'dens_organicsolvent': 818,
    'dissol_cons': 0.052,
    'T_Liprec': 83,
    'T_deion1': 80,
    'T_dissol': 10,
    'T_RO': 40,
    'T_evap': 70,
    'T_desorp': 40,
    'T_adsorp': 85,
    'T_boron': 10,
    'T_Mg_soda': 60,
    'T_motherliq': 80,
    'T_nano': 45,
    'T_IX': 70,
    'adsorp_capacity': 0.008,
    'adsorb_capacity_salar': 0.02 / (1 / 1.2),
    'Li_out_adsorb': 10000,
    'Li_out_RO': 5000,
    'Li_in_RO': 2500,
    'Li_out_evaporator_geothermal': 30000,
    'Li_out_EP_DLE': 2.3,
    'eff_pw': 0.95,
    'heat_loss': 0.85,
    'proxy_freshwater_EP': 0.002726891764265545,
    'proxy_harvest': 8.565755621167364e-05,
    'proxy_saltremoval': 40,
    'proxy_salt_ATACAMA': 1058549010,
    'proxy_quicklime_OLAROZ': 51005000 / (0.17 * 0.180 * 60 * 60 * 24 * 365 * 1300),
    'pH_ini': 11,
    'pOH_ini': 14 - 11,
    'pH_aft': 1.8,
    'pOH_aft': 14 - 1.8,
    'recycling_rate': 0.985,
    'sodiumhydroxide_solution': 0.3,
    'sodaash_solution': 0.25,
    'calciumchloride_solution': 0.3,
    'sulfuricacid_solution': 0.18,
    'Mg_conc_pulp_quicklime': 0.05,
    'quicklime_reaction_factor': 1.2,
    'sodiumhydroxide_reaction_factor': 1.2,
    'sodaash_reaction_factor': 1.3,
    'waste_ratio': 0.1,
    'evaporator_gor': 16,
    'working_hours_excavator': 37,
    'Ca_left_over': 0.0002,
    'elec_IX_factor': 0.82 * 10 ** (-3),
    'water_IX_factor': 1.1,
    'HCl_IX_factor': 0.24 * 10 ** (-3),
    'NaOH_IX_factor': 0.12 * 10 ** (-3),
    'heat_IX_factor': -1.62 * 10 ** (-3),
    'Cl_IX_factor': -0.23 * 10 ** (-3),
    'Na_IX_factor': -0.07 * 10 ** (-3),
    'motherliq_factor': 5,
    'elec_nano_factor' : 4.68 / 0.567,
    'm_output_factor' : 1 / 20,
    'elec_osmosis_factor' : 2.783,
    'E_evap_factor' : 145,  # MJ per m3 input
    'elec_evap_factor' : 2,  # kWh per m3 input
    'evaporator_steam_factor' : 0.2,
    'CO2_factor': 10.0,
    'washing_factor': 2,
    'centrifuge_TG_prod_factor' : 1.5,
    'centrifuge_TG_waste_liquid_factor' : -0.8,
    'centrifuge_TG_recycle_factor' : 0.2,
    'centrifuge_BG_prod_factor' : 1.5,
    'centrifuge_BG_waste_liquid_factor' : -1,
    'centrifuge_wash_prod_factor' : 1.5,
    'centrifuge_wash_waste_liquid_factor' : -1,
    'centrifuge_electricity': 0.01,
    'beltfilter_electricity' : 0.4,
    'rotarydryer_heat' : 0.3,  # Default thermal energy factor
    'rotarydryer_electricity' : 1,  # Default electricity factor
    'rotarydryer_waste_heat' : 0.5,  # Default waste heat factor
    'water_purification_waste_factor' : 0.25,
    'water_purification_new_factor' : 0.25,
    'water_purification_elec_factor' : 2.783,
    'water_adsorption_factor': 100,
    'electricity_adsorption':0.73873739 * 10 ** (-3)
}


SENSITIVITY_RANGES = {
    'dissol_cons': [0.03, 0.04, 0.05, 0.06, 0.07],
    'T_Liprec': [40, 60, 80, 90],
    'heat_loss': [0.3, 0.6, 0.90],
    'T_deion1': [50, 75, 100],
    'T_dissol': [5,  15,  50],
    'T_RO': [20, 40,  80],
    'T_evap': [50, 70, 90],
    'T_desorp': [30, 50, 90],
    'T_adsorp': [40, 60, 80, 100],
    'T_boron': [5, 15, 35],
    'T_Mg_soda': [30, 50, 70, 90],
    'T_motherliq': [30, 50, 70, 90],
    'T_nano': [30, 50, 70, 90],
    'T_IX': [30, 50, 70, 90],
    'adsorp_capacity': [0.005, 0.008, 0.01, 0.03,0.6, 1.0, 10],
    'adsorp_capacity_salar': [0.005, 0.008, 0.01, 0.03,0.6, 1.0, 10],
    'Li_out_adsorb': [5000, 10000, 15000],
    'Li_out_RO': [2500, 5000, 7500, 10000],
    'Li_in_RO': [2000, 2250, 2500, 2750, 3000],
    'Li_out_evaporator_geothermal': [20000, 25000, 30000, 35000, 40000],
    'Li_out_EP_DLE': [1.8, 2.0, 2.2, 2.4, 2.6],
    'eff_pw': [0.5, 0.7, 0.9, 1.0],
    'proxy_freshwater_EP': [0.002, 0.003, 0.004, 0.005],
    'proxy_harvest': [0.00005, 0.00006, 0.00007, 0.00008],
    'proxy_saltremoval': [20, 40, 80, 100],
    'proxy_salt_ATACAMA': [1000000000, 1050000000, 1100000000, 1150000000],
    'proxy_quicklime_OLAROZ': [0.01, 0.04, 0.8, 0.12],
    'pH_ini': [8, 9, 10, 11, 12, 13],
    'pH_aft': [2.0, 3.0, 4.0 , 5.0],
    'recycling_rate': [0.7, 0.8, 0.9, 0.99],
    'sodiumhydroxide_solution': [0.2, 0.4, 0.6, 0.8, 1.0],
    'sodaash_solution': [0.2, 0.4, 0.6, 0.8, 1.0],
    'calciumchloride_solution': [0.2, 0.4, 0.6, 0.8, 1.0],
    'sulfuricacid_solution': [0.2, 0.4, 0.6, 0.8, 1.0],
    'Mg_conc_pulp_quicklime': [0.04, 0.05, 0.06, 0.07],
    'quicklime_reaction_factor': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
    'sodiumhydroxide_reaction_factor': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
    'sodaash_reaction_factor': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
    'evaporator_gor': [10, 12, 14, 16, 18, 20],
    'working_hours_excavator': [20, 30, 37, 40, 50],
    'waste_ratio': [0.1, 0.3, 0.5, 0.7, 0.9],
    'Ca_left_over': [0.0001, 0.0002, 0.0003, 0.0004, 0.0005],
    'motherliq_factor': [1, 3, 5, 7, 9],
    'elec_IX_factor': [0.41 * 10 ** (-3), 0.82 * 10 ** (-3), 1.64 * 10 ** (-3), 2.46 * 10 ** (-3), 3.28 * 10 ** (-3)],
    'water_IX_factor': [0.55, 1.1, 2.2, 3.3, 4.4],
    'HCl_IX_factor': [0.12 * 10 ** (-3), 0.24 * 10 ** (-3), 0.48 * 10 ** (-3), 0.72 * 10 ** (-3), 0.96 * 10 ** (-3)],
    'NaOH_IX_factor': [0.06 * 10 ** (-3), 0.12 * 10 ** (-3), 0.24 * 10 ** (-3), 0.36 * 10 ** (-3), 0.48 * 10 ** (-3)],
    'heat_IX_factor': [-0.81 * 10 ** (-3), -1.62 * 10 ** (-3), -3.24 * 10 ** (-3), -4.86 * 10 ** (-3), -6.48 * 10 ** (-3)],
    'Cl_IX_factor': [-0.115 * 10 ** (-3), -0.23 * 10 ** (-3), -0.46 * 10 ** (-3), -0.69 * 10 ** (-3), -0.92 * 10 ** (-3)],
    'Na_IX_factor': [-0.035 * 10 ** (-3), -0.07 * 10 ** (-3), -0.14 * 10 ** (-3), -0.21 * 10 ** (-3), -0.28 * 10 ** (-3)],
    'elec_nano_factor': [0.5 * (4.68 / 0.567), 1.0 * (4.68 / 0.567), 2.0 * (4.68 / 0.567)],
    'm_output_factor': [0.5 * (1 / 20), 1.0 * (1 / 20), 2.0 * (1 / 20)],
    'elec_osmosis_factor': [0.5 * 2.783, 1.0 * 2.783, 2.0 * 2.783, 3.0 * 2.783, 5.0 * 2.783],
    'E_evap_factor' : [0.5 * 145,1.0 * 145,2.0 * 145,5.0 * 145],
    'elec_evap_factor' : [0.5 * 2,1.0 * 2,2.0 * 2,5.0 * 2],
    'evaporator_steam_factor' : [0.1,0.2,0.4,0.6,0.8],
    'CO2_factor': [5.0, 10.0, 20.0],
    'washing_factor': [1 , 2, 4, 6, 8],
    'centrifuge_electricity': [0.005, 0.01, 0.02, 0.03, 0.04],
    'beltfilter_electricity' : [0.2, 0.4, 0.6, 0.8, 1.0],
    'rotarydryer_heat' : [3.5, 7, 14],  # Sensitivity ranges for thermal energy factor
    'rotarydryer_electricity' : [0.15, 0.3, 0.6],  # Sensitivity ranges for electricity factor
    'rotarydryer_waste_heat' : [0.25, 0.5, 1],  # Sensitivity ranges for waste heat factor
    'water_purification_waste_factor' : [0.25,0.5,0.75,1],
    'water_purification_new_factor' : [0.25,0.5,0.75,1],
    'water_purification_elec_factor' : [1.3915,2.783,5.566,8.349,11.132],
    'water_adsorption_factor': [1, 5, 10, 50, 100, 600],
    'electricity_adsorption': [0.2 * 0.73873739 * 10 ** (-3), 0.73873739 * 10 ** (-3), 3 * 0.73873739 * 10 ** (-3)]
}

SENSITIVITY_RANGES_OLD= {
    'proxy_saltremoval' : [20,40,80,100],
    }


# Define custom percentages for each parameter
custom_percentages = {
    'annual_airtemp': 0.2,
    'density_brine': 0.2,
    'density_enriched_brine': 0.2,
    'lifetime': 0.5,
    'Li_efficiency': 0.20,
    'brine_vol': 0.3,
    'well_depth_brine': 0.5,
    'distance_to_processing': 0.5,
    'production': 0.5,
    'evaporation_rate': 0.20
}


if __name__ == '__main__' :
    import pandas as pd

    # Convert DEFAULT_CONSTANTS to DataFrame
    df_constants = pd.DataFrame(list(DEFAULT_CONSTANTS.items()), columns=['Constant', 'Value'])

    # Convert SENSITIVITY_RANGES to DataFrame
    df_sensitivity = pd.DataFrame(list(SENSITIVITY_RANGES.items()), columns=['Parameter', 'Range'])

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter('sensitivity_values.xlsx', engine='xlsxwriter') as writer:
        # Write each DataFrame to a different worksheet.
        df_constants.to_excel(writer, sheet_name='DEFAULT_CONSTANTS', index=False)
        df_sensitivity.to_excel(writer, sheet_name='SENSITIVITY_RANGES', index=False)

    print("Excel file created successfully.")

