# operational_and_environmental_constants.py


DEFAULT_CONSTANTS={
    # Physical constants
    'H' : 1.008,
    'Mg' : 24.31,
    'B' : 10.81,
    'S' : 32.07,
    'Ca' : 40.08,
    'Li' : 6.94,
    'C' : 12.011,
    'O' : 15.999,
    'Na' : 22.99,
    'Cl' : 35.45,
    'K' : 39.098,
    'Si' : 28.085,
    'As' : 74.922,
    'Mn' : 54.938,
    'Fe' : 55.845,
    'Zn' : 65.38,
    'Ba' : 137.33,
    'Sr' : 87.62,
    'gravity_constant' : 9.81,
    'hCC' : 849,
    'hCH' : 1996,
    'hCHH' : 4190,
    'hCHH_bri' : 3219.94,
    'hCLi' : 1341,
    'heat_natgas' : 40.4,
    'heat_propgas' : 44.33,
    'latheat_H' : 2257000,
    'dens_NaCl' : 2160,
    'dens_Soda' : 2540,
    'dens_CaCl' : 2150,
    'dens_Licarb' : 2100,
    'dens_H2O' : 1000,
    'dens_pulp' : 2 / 3 * 1000 + 1 / 3 * 2100,
    'dens_frw' : 1100,
    'dens_organicsolvent' : 818,
    # Parameters derived from patents
    'dissol_cons' : 0.052, # Source: Wilkomirsky (1999), Perez et al. (2014)
    'T_Liprec' : 83, # Source: Wilkomirsky (1999), Tran & Luong (2015), °C
    'T_dissol' : 10, # Source: Wilkomirsky (1999), °C
    'T_boron' : 10,  # Source: Wilkomirsky (1999), °C
    'T_Mg_soda' : 60, # Source: Wilkomirsky (1999), °C
    'T_motherliq' : 80, # Source: Wilkomirsky (1999), °C
    'Li_out_RO' : 5000, # Source: Featherstone et al. (2019), ppm
    'Li_in_RO' : 2500, # Source: Featherstone et al. (2019), ppm
    'Li_out_evaporator_geothermal' : 30000, # Source: Featherstone et al. (2019), ppm
    'pH_ini' : 11, # Source: Perezz et al (2014)
    'pH_aft' : 1.8, # Source: Perez et al (2014)
    'Mg_conc_pulp_quicklime' : 0.05, # Source: Wilkomirsky (1999), wt. %
    'Ca_left_over' : 0.0002, # Source: Featherstone et al. (2019), wt. %
    'motherliq_factor' : 5, # Source: Wilkomirsky (1999)
    'CO2_factor' : 10.0, # Source: Ehren et al. (2018)
    'washing_factor' : 2, # Source: Ehren et al. (2018)
    'sodaash_solution' : 0.25, # Source: Wilkomirsky (1999) & Ehren et al. (2018)
    # Parameters derived from scientific literature or/and technical reports
    'T_RO' : 40, # Source: Shaheen et al. (2024), °C
    'T_evap' : 70, # Source: Al-Karaghouli et al. (2019), °C
    'T_desorp' : 40, # Source: Lanke Lithium (2018), °C
    'T_adsorp' : 85, # Source: Vera et al. (2023), °C
    'T_nano' : 45, # Source: Li et al. (2020), °C
    'T_IX' : 70, # Source: Ecoinvent (2008), °C
    'Li_out_adsorb' : 10000,  # Source: Vera et al (2023), ppm
    'T_ED' : 25, # Source: Patel et al. (2021)
    'adsorp_capacity_geothermal' : 0.008, # Source: Isupov et al. (1999), wt. %
    'adsorp_capacity_salar' : 0.024, # Source: Tres Quebradas Technical Report
    'Li_out_EP_DLE' : 2.3, # Source: Livent (2024), wt. %
    'eff_pw' : 0.95, # Source
    'heat_loss' : 0.85, # Source: US Department of Energy Efficiency and Renewable Energy (2003), %
    'recycling_rate' : 0.985, # Source: Personal communication (2021)
    'BWI_grinding' : 13,
    'initial_size_grinding' : 1000,
    'final_size_grinding' : 75,
    'efficiency_grinding' : 0.8,
    'water_usage_grinding' : 1.5,
    'waste_grinding_ratio' : 0.1,
    'sodiumhydroxide_solution' : 0.3, # Source: Market data (2024), wt. %
    'calciumchloride_solution' : 0.3, # Source: Market data (2024), wt. %
    'sulfuricacid_solution' : 0.18, # Source: Market data (2024), wt. %
    'quicklime_reaction_factor' : 1.2, # Source: Li et al. (2020)
    'sodiumhydroxide_reaction_factor' : 1.2, # Source: Li et al. (2020)
    'sodaash_reaction_factor' : 1.3, # Source: Li et al. (2020)
    'evaporator_gor' : 16, # Source: Al-Karaghouli et al. (2019)
    'working_hours_excavator' : 37, # Source: Ecoinvent (2020)
    'elec_IX_factor' : 0.82 * 10 ** (-3), # Source: Ecoinvent (2020)
    'water_IX_factor' : 1.1, # Source: Ecoinvent (2020)
    'HCl_IX_factor' : 0.24 * 10 ** (-3), # Source: Ecoinvent (2020)
    'NaOH_IX_factor' : 0.12 * 10 ** (-3), # Source: Ecoinvent (2020)
    'heat_IX_factor' : -1.62 * 10 ** (-3), # Source: Ecoinvent (2020)
    'Cl_IX_factor' : -0.23 * 10 ** (-3), # Source: Ecoinvent (2020)
    'Na_IX_factor' : -0.07 * 10 ** (-3), # Source: Ecoinvent (2020)
    'elec_nano_factor' : 4.68 / 0.567, # Source: Li et al. (2020)
    'elec_osmosis_factor' : 2.783, # Source: Ecoinvent (2008), kWh per kg
    'E_evap_factor' : 145,  # Source: Al-Karaghouli et al. (2019), MJ per m3 input
    'elec_evap_factor' : 2,  # Source: Al-Karaghouli et al. (2019), kWh per m3 input
    'evaporator_steam_factor' : 0.2, # Source: Al-Karaghouli et al. (2019)
    'beltfilter_electricity' : 0.4, # Source: Piccino et al. (2016), kWh per kg
    'rotarydryer_heat' : 0.3,  # Default thermal energy factor
    'rotarydryer_electricity' : 1,  # Default electricity factor
    'rotarydryer_waste_heat' : 0.5,  # Default waste heat factor
    'water_adsorption_factor' : 100, # Source: Goldberg et al. (2022)
    'electricity_adsorption' : 0.73873739 * 10 ** (-3), # Source: Ecoinvent (2020)
    'centrifuge_electricity' : 0.01, # Source: Piccinno et al. (2016), kWh per kg
    'water_purification_elec_factor' : 2.783, # Source: Ecoinvent (2008), kWh per m3 input
    # Parameters derived from proxies
    'proxy_freshwater_EP' : 0.002726891764265545, #Source: SQM data (2018) - water (EP) per kg of precipitated salt
    'proxy_harvest' : 8.565755621167364e-05,
    'proxy_saltremoval' : 40,
    'proxy_salt_ATACAMA' : 1058549010, # Source: SQM data (2018) - salt precipitates (Atacama)
    'proxy_quicklime_OLAROZ' : 51005000 / (0.17 * 0.180 * 60 * 60 * 24 * 365 * 1300), # Source: Quicklime demand (Orocobre, 2018) per kg of Mg in brine
    # Parameters with no data
    'proxy_salt_carbonate_ratio' : 0.15,
    'proxy_moisture_precipitated_salt' : 0.1,
    'water_coverage_evaporationponds' : 0.1,
    'waste_ratio' : 0.1,
    'm_output_factor' : 1 / 20,
    'salinity_ED' : 1,
    'removal_fraction_ED' : 0.9,
    'washing_general_waste_ratio' : 0.1,
    'centrifuge_TG_prod_factor' : 1.5,
    'centrifuge_TG_waste_liquid_factor' : -0.8,
    'centrifuge_TG_recycle_factor' : 0.2,
    'centrifuge_BG_prod_factor' : 1.5,
    'centrifuge_BG_waste_liquid_factor' : -1,
    'centrifuge_wash_prod_factor' : 1.5,
    'centrifuge_wash_waste_liquid_factor' : -1,
    'water_purification_waste_factor' : 0.25,
    'water_purification_new_factor' : 0.25
    }

SENSITIVITY_RANGES = {
    'dissol_cons': [ 0.0052, 0.0208, 0.0312, 0.052, 0.07279999999999999, 0.0832, 0.09879999999999999 ],
    'T_Liprec': [ 20, 40, 60, 80, 90 ], 'T_dissol': [ 5, 15, 35 ], 'T_boron': [ 5, 10, 20 ],
    'T_Mg_soda': [ 50, 60, 70, 80, 90 ], 'T_motherliq': [ 60, 70, 80, 90, 100 ],
    'Li_out_RO': [ 2500, 5000, 7500, 10000 ], 'Li_in_RO': [ 2000, 2250, 2500, 2750, 3000 ],
    'Li_out_evaporator_geothermal': [ 20000, 25000, 30000, 35000, 40000 ],
    'pH_ini': [ 14, 12, 11, 10, 9, 8 ],
    'pH_aft': [ 1.8, 3, 4, 5, 6 ],
    'Mg_conc_pulp_quicklime': [ 0.005000000000000001, 0.020000000000000004, 0.03, 0.05, 0.06999999999999999,
                                0.08000000000000002, 0.095 ],
    'Ca_left_over': [ 2e-05, 8e-05, 0.00012, 0.0002, 0.00028, 0.00032, 0.00038 ],
    'motherliq_factor': [ 0.5, 2.0, 3.0, 5, 7.0, 8.0, 9.5 ], 'CO2_factor': [ 1.0, 4.0, 6.0, 10.0, 14.0, 16.0, 19.0 ],
    'washing_factor': [ 0.2, 0.8, 1.2, 2, 2.8, 3.2, 3.8 ], 'sodaash_solution': [ 0.2, 0.25, 0.3 ],
    'T_RO': [ 20, 30, 40, 50, 60 ], 'T_evap': [ 50, 60, 70, 80, 90 ], 'T_desorp': [ 20, 30, 40, 50, 60 ],
    'T_adsorp': [ 65, 75, 85, 95 ], 'T_nano': [ 25, 35, 45, 55, 65 ], 'T_IX': [ 50, 60, 70, 80, 90 ],
    'Li_out_adsorb': [ 1000.0, 4000.0, 6000.0, 10000, 14000.0, 16000.0, 19000.0 ], 'T_ED': [ 5, 15, 25, 35, 45 ],
    'adsorp_capacity_geothermal': [ 0.0591, 0.01922, 0.0326, 0.012, 0.0069, 0.00974, 0.01332, 0.02835, 0.02933, 0.0311,
                                    0.01135, 0.0155, 0.0114 ],
    'adsorp_capacity_salar': [ 0.0591, 0.01922, 0.0326, 0.012, 0.0069, 0.00974, 0.01332, 0.02835, 0.02933, 0.0311,
                               0.01135, 0.0155, 0.0114 ],
    'Li_out_EP_DLE': [ 0.22999999999999998, 0.9199999999999999, 1.38, 2.3, 3.2199999999999998, 3.6799999999999997,
                       4.369999999999999 ], 'eff_pw': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.95 ],
    'heat_loss': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.85 ], 'recycling_rate': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.985 ],
    'BWI_grinding': [ 1.3, 5.2, 7.8, 13, 18.2, 20.8, 24.7 ],
    'initial_size_grinding': [ 100.0, 400.0, 600.0, 1000, 1400.0, 1600.0, 1900.0 ],
    'final_size_grinding': [ 7.5, 30.0, 45.0, 75, 105.0, 120.0, 142.5 ],
    'efficiency_grinding': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.8 ],
    'water_usage_grinding': [ 0.15000000000000002, 0.6000000000000001, 0.8999999999999999, 1.5, 2.0999999999999996,
                              2.4000000000000004, 2.8499999999999996 ],
    'waste_grinding_ratio': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.1 ],
    'sodiumhydroxide_solution': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.3 ],
    'calciumchloride_solution': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.3 ],
    'sulfuricacid_solution': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.18 ],
    'quicklime_reaction_factor': [ 0.12, 0.48, 0.72, 1.2, 1.68, 1.92, 2.28 ],
    'sodiumhydroxide_reaction_factor': [ 0.12, 0.48, 0.72, 1.2, 1.68, 1.92, 2.28 ],
    'sodaash_reaction_factor': [ 0.13, 0.52, 0.78, 1.3, 1.8199999999999998, 2.08, 2.4699999999999998 ],
    'evaporator_gor': [ 1.6, 6.4, 9.6, 16, 22.4, 25.6, 30.4 ],
    'working_hours_excavator': [ 3.7, 14.8, 22.2, 37, 51.8, 59.2, 70.3 ],
    'elec_IX_factor': [ 8.2e-05, 0.000328, 0.0004919999999999999, 0.00082, 0.001148, 0.001312, 0.001558 ],
    'water_IX_factor': [ 0.11000000000000001, 0.44000000000000006, 0.66, 1.1, 1.54, 1.7600000000000002, 2.09 ],
    'HCl_IX_factor': [ 2.4e-05, 9.6e-05, 0.000144, 0.00024, 0.000336, 0.000384, 0.00045599999999999997 ],
    'NaOH_IX_factor': [ 1.2e-05, 4.8e-05, 7.2e-05, 0.00012, 0.000168, 0.000192, 0.00022799999999999999 ],
    'heat_IX_factor': [ -0.00016200000000000003, -0.0006480000000000001, -0.000972, -0.0016200000000000001, -0.002268,
                        -0.0025920000000000006, -0.003078 ],
    'Cl_IX_factor': [ -2.3000000000000003e-05, -9.200000000000001e-05, -0.000138, -0.00023, -0.00032199999999999997,
                      -0.00036800000000000005, -0.000437 ],
    'Na_IX_factor': [ -7.000000000000001e-06, -2.8000000000000003e-05, -4.2000000000000004e-05, -7.000000000000001e-05,
                      -9.800000000000001e-05, -0.00011200000000000001, -0.000133 ],
    'elec_nano_factor': [ 0.8253968253968256, 3.3015873015873023, 4.9523809523809526, 8.253968253968255,
                          11.555555555555555, 13.20634920634921, 15.682539682539684 ],
    'elec_osmosis_factor': [ 0.2783, 1.1132, 1.6698, 2.783, 3.8961999999999994, 4.4528, 5.287699999999999 ],
    'E_evap_factor': [ 14.5, 58.0, 87.0, 145, 203.0, 232.0, 275.5 ],
    'elec_evap_factor': [ 0.2, 0.8, 1.2, 2, 2.8, 3.2, 3.8 ],
    'evaporator_steam_factor': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.2 ],
    'beltfilter_electricity': [ 0.04000000000000001, 0.16000000000000003, 0.24, 0.4, 0.5599999999999999,
                                0.6400000000000001, 0.76 ],
    'rotarydryer_heat': [ 0.03, 0.12, 0.18, 0.3, 0.42, 0.48, 0.57 ],
    'rotarydryer_electricity': [ 0.1, 0.4, 0.6, 1, 1.4, 1.6, 1.9 ],
    'rotarydryer_waste_heat': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.5 ],
    'water_adsorption_factor': [ 10.0, 40.0, 60.0, 100, 140.0, 160.0, 190.0 ],
    'electricity_adsorption': [ 7.3873739e-05, 0.000295494956, 0.000443242434, 0.00073873739, 0.0010342323459999999,
                                0.001181979824, 0.001403601041 ],
    'centrifuge_electricity': [ 0.002, 0.005, 0.01, 0.02, 0.03 ],
    'proxy_freshwater_EP': [ 0.000545378352853109, 0.0013634458821327724, 0.002726891764265545, 0.00545378352853109,
                             0.008180675292796634 ],
    'proxy_harvest': [ 1.7131511242334727e-05, 4.282877810583682e-05, 8.565755621167364e-05, 0.00017131511242334728,
                       0.0002569726686350209 ], 'proxy_saltremoval': [ 8.0, 20.0, 40, 80, 120 ],
    'proxy_salt_ATACAMA': [ 211709802.0, 529274505.0, 1058549010, 2117098020, 3175647030 ],
    'proxy_quicklime_OLAROZ': [ 0.008131513022282114, 0.020328782555705284, 0.04065756511141057, 0.08131513022282114,
                                0.1219726953342317 ],
    'proxy_salt_carbonate_ratio': [ 0.03, 0.075, 0.15, 0.3, 0.44999999999999996 ],
    'proxy_moisture_precipitated_salt': [ 0.020000000000000004, 0.05, 0.1, 0.2, 0.30000000000000004 ],
    'water_coverage_evaporationponds': [ 0.020000000000000004, 0.05, 0.1, 0.2, 0.30000000000000004 ],
    'waste_ratio': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.1 ],
    'm_output_factor': [ 0.010000000000000002, 0.025, 0.05, 0.1, 0.15000000000000002 ],
    'salinity_ED': [ 0.2, 0.5, 1, 2, 3 ], 'removal_fraction_ED': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.9 ],
    'washing_general_waste_ratio': [ 0.1, 0.3, 0.5, 0.7, 0.9, 1, 0.1 ],
    'centrifuge_TG_prod_factor': [ 0.30000000000000004, 0.75, 1.5, 3.0, 4.5 ],
    'centrifuge_TG_waste_liquid_factor': [ -0.1, -0.3, -0.5, -0.7, -0.9, -1, -0.8 ],
    'centrifuge_TG_recycle_factor': [ 0.04000000000000001, 0.1, 0.2, 0.4, 0.6000000000000001 ],
    'centrifuge_BG_prod_factor': [ 0.30000000000000004, 0.75, 1.5, 3.0, 4.5 ],
    'centrifuge_BG_waste_liquid_factor': [ -0.1, -0.3, -0.5, -0.7, -0.9, -1, -1 ],
    'centrifuge_wash_prod_factor': [ 0.30000000000000004, 0.75, 1.5, 3.0, 4.5 ],
    'centrifuge_wash_waste_liquid_factor': [ -0.1, -0.3, -0.5, -0.7, -0.9, -1, -1 ]}







if __name__ == '__main__' :
    import pandas as pd
    import json

    # Output the updated dictionary in a copy-paste-ready format
    sensitivity_ranges_output=json.dumps(SENSITIVITY_RANGES, indent=4)
    sensitivity_ranges_output

    # Convert DEFAULT_CONSTANTS to DataFrame
    df_constants=pd.DataFrame(list(DEFAULT_CONSTANTS.items()), columns=['Constant', 'Value'])

    # Convert SENSITIVITY_RANGES to DataFrame
    df_sensitivity=pd.DataFrame(list(SENSITIVITY_RANGES.items()), columns=['Parameter', 'Range'])

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter('sensitivity_values.xlsx', engine='xlsxwriter') as writer :
        # Write each DataFrame to a different worksheet.
        df_constants.to_excel(writer, sheet_name='DEFAULT_CONSTANTS', index=False)
        df_sensitivity.to_excel(writer, sheet_name='SENSITIVITY_RANGES', index=False)

    print("Excel file created successfully.")
