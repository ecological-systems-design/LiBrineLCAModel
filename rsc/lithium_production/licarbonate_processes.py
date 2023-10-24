from rsc.lithium_production.chemical_formulas import *

from rsc.lithium_production.operational_data_salton import *

import pandas as pd
import os
import logging
import inspect
import json
import datetime

if not os.path.exists("../../images") :
    os.mkdir("../../images")


# Si & Fe removal by precipitation
class SiFe_removal_limestone :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_SiFe_removal_limestone'  # Si and Fe removal by precipitation
        vec_end = site_parameters['vec_end']
        E_SiFe = 0
        Fe_mass = (vec_end[-5] / 100) * m_in
        Si_mass = vec_end[-8] / 100 * m_in
        limestone_Fe = (Fe_mass / Fe) * (Ca + C + 3 * O) * 1.1 + Si_mass / Si * (
                Ca + C + 3 * O) * 1.1  # efficiency assumed to be 0.9
        waste_FeSi = -(Fe_mass / Fe) * (3 * Ca + 2 * Fe + 3 * Si + 12 * O)
        m_output = m_in + waste_FeSi + limestone_Fe  # + limestone_Si

        df_data = {
            'Variables' : [f'm_output_{process_name}', f'm_Li_{process_name}', f'E_{process_name}',
                           f'chemical_limestone_{process_name}', f'waste_solid_{process_name}'],
            'Values' : [m_output, m_in * vec_end[0] / 100, E_SiFe, limestone_Fe, waste_FeSi]
            }

        df_process = pd.DataFrame(df_data)
        df_process['per kg'] = df_process['Values'] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]['Values']

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Mn and Zn removal by precipitation
class MnZn_removal_lime :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_MnZn_removal_lime'
        vec_end = site_parameters['vec_end']  # vector of chemical composition of brine
        E_MnZn = 0  # Heating necessary?

        Mn_mass = vec_end[-6] / 100 * m_in
        Zn_mass = vec_end[-4] / 100 * m_in

        lime_MnZn = (Mn_mass / Mn + Zn_mass / Zn) * (Ca + 2 * (O + H)) * 1.2
        water_lime = (lime_MnZn / (Ca + O)) * (H * 2 + O)

        waste_Mn = -(Mn_mass / Mn * (Mn + 2 * (O + H)))
        waste_Zn = -(Zn_mass / Zn * (Zn + 2 * (O + H)))
        waste_sum = waste_Mn + waste_Zn

        Ca_mass_brine = Ca / (Ca + C + 3 * O) * lime_MnZn  # Calculating mass of Ca in brine # dH calculating
        m_output = m_in + waste_Mn + waste_Zn + Ca_mass_brine + lime_MnZn + water_lime  # mass of brine as output

        df_data = {
            'Variables' : [f'm_output_{process_name}', f'm_in_{process_name}', f'E_{process_name}',
                           f'chemical_lime_{process_name}',
                           f'water_{process_name}', f'waste_solid_{process_name}',
                           f'Ca_mass_{process_name}'],
            'Values' : [m_output, m_in, E_MnZn, lime_MnZn, water_lime, waste_sum, Ca_mass_brine]
            }

        df_process = pd.DataFrame(df_data)
        df_process['per kg'] = df_process['Values'] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]['Values']

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : Ca_mass_brine
            }


# acidification & ion exchanger, T = 30 - 100 °C, pH adaption
class acidification :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_acidification'
        Dens_ini = site_parameters['density_brine']  # density of brine
        vec_end = site_parameters['vec_end']  # vector of chemical composition of brine
        # pH adaption
        pH_ini = 8  # Initial pH of concentrated brine
        pOH_ini = 14 - pH_ini  # Initial pOH of concentrated brine
        pH_aft = 4.5  # End pH of concentrated brine by adding HCl solution
        pOH_aft = 14 - pH_aft  # End pOH of concentrated brine by adding HCl solution

        delta_H_conc = (10 ** -pH_aft) - (10 ** -pH_ini)  # Difference of number of H+ in brine
        delta_OH_conc = (10 ** -pOH_ini) - (10 ** -pOH_aft)  # Difference of number OH- in brine

        HCl_pH = (((
            (delta_H_conc * (m_in / (1000 * Dens_ini)) * (H + Cl) + delta_OH_conc * (m_in / (Dens_ini * 1000)) * (
                    H + Cl)))) / 0.32)  # Required mass of 32 wt. % HCl solution to reduce pH [kg]
        HCl_borate = ((vec_end[7] * 10 * m_in / B) * 1 * (
                H * Cl) / 1000) / 0.32  # Required mass of HCl to overcome the buffering effect of borate [kg]
        HCl_sulfate = ((vec_end[6] * 10 * m_in / (S + O * 4)) * 0.56 * (
                H * Cl) / 1000) / 0.32  # Required mass of HCl to overcome the buffering effect of sulfate [kg]

        HCl_mass32 = (HCl_pH + HCl_borate + HCl_sulfate) * 0.32  # Total required mass of 32 wt. % HCl solution [kg]
        m_output = m_in + HCl_mass32

        df_data = {
            'Variables' : [f'm_output_{process_name}', f'm_in_{process_name}', f'chemical_HCl_{process_name}'],
            'Values' : [m_output, m_in, HCl_mass32]
            }

        df_process = pd.DataFrame(df_data)
        df_process['per kg'] = df_process['Values'] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]['Values']

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Li-ion selective adsorption
class Li_adsorption :
    def execute(self, prod, site_parameters, m_in) :
        process_name = 'df_Li_adsorption'
        life = site_parameters['lifetime']  # lifetime of the plant
        T_out = site_parameters['annual_airtemp']  # annual air temperature
        adsorbent_loss = prod * ((2 * Li) / (2 * Li + C + 3 * O)) * 1.25
        adsorbent_invest = prod * ((2 * Li) / (2 * Li + C + 3 * O)) / adsorp_capacity
        adsorbent = (adsorbent_invest / life) + adsorbent_loss
        water_adsorbent = 100 * adsorbent_invest
        elec_adsorp = 0.73873739 * 10 ** (-3) * (
                m_in + water_adsorbent
        )  # Electricity demand for ion exchanger [kWh]

        E_adsorp = (
                           ((T_adsorp - T_out) * hCHH * water_adsorbent) / 10 ** 6
                   ) / heat_loss

        m_output = water_adsorbent

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"chemical_adsorbent_{process_name}",
                f"water_adsorbent_{process_name}",
                f"elec_adsorp_{process_name}",
                f"E_adsorp_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                adsorbent,
                water_adsorbent,
                elec_adsorp,
                E_adsorp,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }
    def update_adsorption(df_adsorption, water_RO, water_evap, df_reverse_osmosis, df_triple_evaporator, T_desorp,
                             hCHH,
                             heat_loss, site_parameters) :
        T_out = site_parameters['annual_airtemp']  # annual air temperature
        new_value = df_adsorption.iloc[3, 1] - water_RO - water_evap
        df_adsorption.loc[3, 'Values'] = new_value

        new_value_kg = df_adsorption.iloc[3, 2] - (water_RO / df_adsorption.iloc[0, 1]) - (
                water_evap / df_adsorption.iloc[0, 1])
        df_adsorption.loc[3, 'per kg'] = new_value_kg

        backflow_ro = df_reverse_osmosis.iloc[1, 1] - df_reverse_osmosis.iloc[0, 1]
        df_reverse_osmosis.loc[len(df_reverse_osmosis.index)] = ['backflow_ro', backflow_ro, 0]

        backflow_evap = df_triple_evaporator.iloc[1, 1] - df_triple_evaporator.iloc[0, 1]
        df_triple_evaporator.loc[len(df_triple_evaporator.index)] = ['backflow_evap', backflow_evap, 0]

        E_adsorp_adapted = (((T_desorp - T_out) * hCHH * df_adsorption.iloc[3, 1]) / 10 ** 6) / heat_loss
        df_adsorption.loc[5, 'Values'] = E_adsorp_adapted
        df_adsorption.loc[5, 'per kg'] = E_adsorp_adapted / df_adsorption.iloc[0, 1]

        return df_adsorption, df_reverse_osmosis, df_triple_evaporator


class CaMg_removal_sodiumhydrox :
    def execute(self, Ca_mass_leftover, site_parameters, m_in) :
        process_name = 'df_CaMg_removal_sodiumhydrox'
        vec_end = site_parameters['vec_end']  # vector of chemical composition of brine
        left_over = 0.0002
        Ca_mass = left_over * (vec_end[4] / 100 * m_in + Ca_mass_leftover)
        Mg_mass = left_over * vec_end[5] / 100 * m_in
        Ba_mass = left_over * vec_end[-1] / 100 * m_in
        Sr_mass = left_over * vec_end[-3] / 100 * m_in

        NaOH = (Mg_mass / Mg + Ba_mass / Ba + Sr_mass / Sr) * 2 * (Na + O + H) * 1.2
        water_NaOH = NaOH / (Na + O + H) * (2 * H + O) * 1.2  # with process water

        sodaash_Ca = Ca_mass / Ca * (2 * Na + C + 3 * O)
        water_sodaash_Ca = sodaash_Ca / 0.25  # with process water
        water_sum = water_sodaash_Ca + water_NaOH

        waste_MgBaSr = -((Mg_mass / Mg) * (Mg + 2 * (O + H)) + (Ba_mass / Ba) * (Ba + 2 * (O + H)) + (Sr_mass / Sr) * (
                Sr + 2 * (O + H)))
        waste_Ca = -(Ca_mass / Ca * (Ca + 3 * (C + O)))
        waste_sum = waste_MgBaSr + waste_Ca

        m_output = m_in + NaOH + water_NaOH + sodaash_Ca + water_sodaash_Ca + waste_MgBaSr + waste_Ca

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"NaOH_{process_name}",
                f"water_sum_{process_name}",
                f"chemical_sodaash_{process_name}",
                f"waste_solid_{process_name}"
                ],
            "Values" : [
                m_output,
                m_in,
                NaOH,
                water_sum,
                sodaash_Ca,
                waste_sum
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }

#Mg removal by soda ash TODO: repair this function
class Mg_removal_soda :
    def execute(self, site_parameters, m_in) :
        process_name = "Mg_removal_soda"
        input_mliq = input('Is mother liquor reported?')

        if input_mliq == 'yes' :
            motherliq = 5 * m_in
            cLi_motherliq = ((0.012 * 6 - 0.058) / 5)
            m_mixbri = m_in + motherliq
            T_mix = (motherliq * 80 + 60 * m_in) / (motherliq + m_in)
            T_Mg = 60

            if T_Mg > T_mix :
                E_Mg = ((T_Mg - T_mix) * hCHH_bri * m_mixbri / 10 ** 6) / heat_loss
                energy.append(E_Mg)
            else :
                E_Mg = 0
                pass
        else :
            E_Mg = 0

        sodaash_Mg = (((vec_end[5] / 100) * m_in) / Mg) * (Na * 2 + C + O * 3) * 1.1
        water_soda_Mg = sodaash_Mg / 0.25
        deion_water.append(water_soda_Mg)

        MgCO3_waste = -(((vec_end[5] / 100) * m_in / Mg) * (Mg + C + O * 3))
        NaCl_waste = -(2 * MgCO3_waste / (Mg + C + O * 3) * (Na + Cl))
        waste_sum = MgCO3_waste + NaCl_waste
        m_output = m_in + water_soda_Mg + MgCO3_waste + NaCl_waste

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"E_{process_name}",
                f"chemical_sodaash_{process_name}",
                f"water_sodaash_{process_name}",
                f"waste_solid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                E_Mg,
                sodaash_Mg,
                water_soda_Mg,
                waste_sum,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }

#Mg removal by quicklime TODO: repair this function
class Mg_removal_quick :
    def execute(self, site_parameters, m_in) :
        process_name = "Mg_removal_quick"

        Mg_lime_ini = 0.05  # in wt. % of the pulp
        lime_high = (((Mg_lime_ini / 100) * m_in) / Mg) * (Ca + O * 2 + H * 2) * 1.2
        water_lime_high = (lime_high / (Ca + O)) * (H * 2 + O)

        waste_Ca = -((lime_high / (Ca + 2 * H + 2 * O)) * (0.66 * (S + Ca + O * 4 + 2 * (H * 2 + O))))
        waste_Mg = -((lime_high / (Ca + 2 * H + 2 * O)) * (Mg + H * 2 + O * 2))
        waste_sum = waste_Ca + waste_Mg
        m_output = water_lime_high + m_in

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"lime_high_{process_name}",
                f"water_lime_high_{process_name}",
                f"waste_solid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                lime_high,
                water_lime_high,
                waste_sum,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


class ion_exchange_L :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_ion_exchange_L'

        elec_IX = 0.82 * 10 ** (-3) * m_in  # Electricity demand for ion exchanger [kWh]
        water_IX = 1.1 * m_in  # Required mass of deionized water [kg]
        HCl_IX = 0.24 * 10 ** (-3) * m_in  # HCl demand for ion exchanger [kg]
        NaOH_IX = 0.12 * 10 ** (-3) * m_in  # NaOH demand for ion exchanger [kg]
        heat_IX = -(1.62 * 10 ** (-3) * m_in)  # Thermal energy waste for ion exchanger [MJ]
        Cl_IX = -(0.23 * 10 ** (-3) * m_in)  # Chlorine waste production [kg]
        Na_IX = -(0.07 * 10 ** (-3) * m_in)  # Sodium waste production [kg]
        m_output = m_in

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"water_{process_name}",
                f"chemical_HCl_{process_name}",
                f"chemical_NaOH_{process_name}",
                f"waste_heat_{process_name}",
                f"waste_Cl_{process_name}",
                f"waste_Na_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                elec_IX,
                water_IX,
                HCl_IX,
                NaOH_IX,
                heat_IX,
                Cl_IX,
                Na_IX,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }

#Ion exchanger - high water demand TODO: repair this function
class ion_exchange_H :
    def execute(self, site_parameters, m_in) :
        process_name = "ion_exchange_H"

        elec_IX = 3 * 0.82 * 10 ** (-3) * m_in  # Electricity demand for ion exchanger [kWh]
        water_IX = 3 * 0.5 * (2 * m_in)  # Required mass of deionized water [kg]
        HCl_IX = 3 * 0.24 * 10 ** (-3) * m_in  # HCl demand for ion exchanger [kg]
        NaOH_IX = 3 * 0.12 * 10 ** (-3) * m_in  # NaOH demand for ion exchanger [kg]
        heat_IX = -(3 * 1.62 * 10 ** (-3) * m_in)  # Thermal energy demand for ion exchanger [MJ]
        Cl_IX = 3 * 0.23 * 10 ** (-3) * m_in  # Chlorine waste production [kg]
        Na_IX = 3 * 0.07 * 10 ** (-3) * m_in  # Sodium waste production [kg]
        m_output = m_in

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"water_{process_name}",
                f"chemical_HCl_{process_name}",
                f"chemical_NaOH_{process_name}",
                f"waste_heat_{process_name}",
                f"waste_Cl_{process_name}",
                f"waste_Na_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                elec_IX,
                water_IX,
                HCl_IX,
                NaOH_IX,
                heat_IX,
                Cl_IX,
                Na_IX,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


class reverse_osmosis :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_reverse_osmosis'

        elec_osmosis = (2.783 * m_in / 1000)  # kWh, based on ecoinvent (2008)
        water_RO = (1 - (Li_in_RO / Li_out_RO)) * m_in
        m_output = Li_in_RO / Li_out_RO * m_in

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"waterother_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                elec_osmosis,
                water_RO,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : water_RO,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


class triple_evaporator :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_triple_evaporator'

        E_evap = m_in / 1100 * 145  # MJ per m3 input
        elec_evap = m_in / 1100 * 2  # kWh per m3 input
        steam = (Li_out_RO / Li_out_evaporator * m_in) / 16  # taking from geothermal power plant
        water_evap = (1 - Li_out_RO / Li_out_evaporator) * m_in
        m_output = Li_out_RO / Li_out_evaporator * m_in

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"E_{process_name}",
                f"elec_{process_name}",
                f"steam_{process_name}",
                f"waterother_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                E_evap,
                elec_evap,
                steam,
                water_evap,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : water_evap,
            'Ca_mass_brine' : None
            }


class Liprec_TG :
    def execute(self, prod, site_parameters, m_in) :
        process_name = 'df_Liprec_TG'
        T_out = site_parameters['annual_airtemp']  # annual air temperature

        E_Liprec = (((T_Liprec - T_out) * hCHH_bri * m_in) /
                    10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        sodaash_Liprec = ((prod * 1000 / (Li * 2 + C + O * 3)) * (Na * 2 + C + O * 3) /
                          1000) / 0.7  # stoichiometrically calculated soda ash demand [kg]
        prod_NaCl2 = (prod * 1000 / (Li * 2 + C + O * 3)) * (Na + Cl) / 1000  # waste production [kg]
        water_sodaash = sodaash_Liprec / 0.2  # water demand to produce 20 vol. % Na2CO3 solution [kg]
        m_output = m_in + sodaash_Liprec + water_sodaash  # output of lithium carbonate precipitation process [kg]

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"E_{process_name}",
                f"chemical_sodaash_{process_name}",
                f"waste_solid_{process_name}",
                f"water_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                E_Liprec,
                sodaash_Liprec,
                prod_NaCl2,
                water_sodaash,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


class dissolution :
    def execute(self, prod, site_parameters, m_in) :
        process_name = "df_dissolution"

        prod_libicarb = prod / (Li * 2 + C + O * 3) * (
                2 * (Li + H + C + O * 3))  # mass of lithiumbicarbonate [kg]
        mass_HCO = prod_libicarb * (H * 2 + C + O * 3) / (
                Li + H + C + O * 3)  # mass of required HCO3- in solution [kg]
        mass_CO2 = (
                           ((C + O * 2) / (H * 2 + C + O * 3)) * mass_HCO
                   ) * 0.6  # mass of required CO2 to dissolve lithium carbonate [kg]
        water_deion2 = (
                prod / 0.052)  # - (prod * 2)  # Required mass of deionized water to dissolve lithium carbonate [kg]
        elec_dissol = 0
        m_output = m_in + water_deion2  # Mass output of dissolution process [kg]

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"water_{process_name}",
                f"elec_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                water_deion2,
                elec_dissol,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : mass_CO2,
            'prod_libicarb' : prod_libicarb,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


class Liprec_BG :
    def execute(self, mass_CO2, prod_libicarb, prod, site_parameters, m_in) :
        process_name = 'df_Liprec_BG'
        boil_point = site_parameters['boilingpoint_process']  # boiling point
        T_out = site_parameters['annual_airtemp']  # annual air temperature

        rel_heat_CO2 = mass_CO2 * hCC * (boil_point - T_out
                                         )  # heat loss due to CO2 release [J]
        rel_heat_H2O = (
                               (H * 2 + O) / (2 * (Li + H + C + O * 3))) * prod_libicarb * hCH * (
                               boil_point - T_out) + (
                               (H * 2 + O) / (2 * (Li + H + C + O * 3))
                       ) * prod_libicarb * latheat_H  # heat loss due to H2O release [J]
        waste_heat_sum = -(rel_heat_CO2 + rel_heat_H2O)
        E_seclicarb = (((
                                (boil_point - T_out) * hCHH * m_in) + rel_heat_CO2 + rel_heat_H2O) /
                       10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        mass_h2o = -((
                             (H * 2 + O) / (2 * (Li + H + C + O * 3))
                     ) * prod_libicarb)  # Mass of H2O lost due to precipitation of Li2CO3 [kg]
        m_output = m_in + mass_h2o + prod - mass_CO2  # Output mass of this process [kg]

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"waste_heat_{process_name}",
                f"E_{process_name}"
                ],
            "Values" : [
                m_output,
                m_in,
                waste_heat_sum,
                E_seclicarb
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Washing Li2CO3 (TG)
class washing_TG :
    def execute(self, prod, site_parameters, m_in) :
        T_out = site_parameters['annual_airtemp']  # annual air temperature
        boil_point = site_parameters['boilingpoint_process']  # boiling point
        water_deion = 2 * prod  # Mass of water required for washing [kg]
        E_deion = (((boil_point - T_out) * hCHH * water_deion) / 10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        m_output = 3.5 * prod  # Mass output of this process [kg]

        process_name = 'df_washing_TG'

        df_data = {
            "Variables" : [f"m_output_{process_name}", f"m_in_{process_name}", f"water_{process_name}",
                           f"E_{process_name}"],
            "Values" : [m_output, m_in, water_deion, E_deion],
            }

        df_process = pd.DataFrame(df_data)
        df_process[f"per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Washing Li2CO3 (BG)
class washing_BG :
    def execute(self, prod, site_parameters, m_in) :
        boil_point = site_parameters['boilingpoint_process']  # boiling point
        T_out = site_parameters['annual_airtemp']  # annual air temperature
        water_deion = 2 * prod  # Mass of water required for washing [kg]
        E_deion = (((boil_point - T_out) * hCHH * water_deion) / 10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        m_output = 3.5 * prod  # Mass output of this process [kg]

        process_name = 'df_washing_BG'

        df_data = {
            "Variables" : [f"m_output_{process_name}", f"m_in_{process_name}", f"water_{process_name}",
                           f"E_{process_name}"],
            "Values" : [m_output, m_in, water_deion, E_deion],
            }

        df_process = pd.DataFrame(df_data)
        df_process[f"per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Centrifuge after TG
class centrifuge_TG :
    def execute(self, prod, site_parameters, m_in) :
        Dens_ini = site_parameters['density_brine']  # initial density of brine
        elec_centri = 1.3 * m_in / (Dens_ini * 1000)  # Electricity consumption of centrifuge [kWh]
        waste_centri = -(0.8 * (m_in - 1.5 * prod)) / 1000
        recycled_waste = 0.2 * (m_in - 1.5 * prod)
        m_output = 1.5 * prod

        process_name = 'df_centrifuge_TG'

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"waste_liquid_{process_name}",
                f"recycled_waste_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                elec_centri,
                waste_centri,
                recycled_waste
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Centrifuge after BG
class centrifuge_BG :
    def execute(self, prod, site_parameters, m_in) :
        Dens_ini = site_parameters['density_brine']  # initial density of brine
        elec_centri = 1.3 * m_in / (Dens_ini * 1000)  # Electricity consumption of centrifuge [kWh]
        waste_centri = -((m_in - 1.5 * prod) / 1000)
        m_output = 1.5 * prod

        process_name = 'df_centrifuge_BG'

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"waste_liquid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                elec_centri,
                waste_centri,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Centrifuge after washing
class centrifuge_wash :
    def execute(self, prod, site_parameters, m_in) :
        Dens_ini = site_parameters['density_brine']  # initial density of brine
        elec_centri = 1.3 * m_in / (Dens_ini * 1000)  # Electricity consumption of centrifuge [kWh]
        waste_centri = -(m_in - 1.5 * prod) / 1000
        m_output = 1.5 * prod

        process_name = 'df_centrifuge_wash'

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"waste_liquid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                elec_centri,
                waste_centri,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Belt filter
class belt_filter :
    def execute(self, prod, site_parameters, m_in) :
        recyc_water = m_in - 1.5 * prod  # No waste is produced because the residual is sent back
        elec_belt = 0.4 * (
                ((m_in - 1.5 * prod) / dens_H2O) + (1.5 * prod / dens_Licarb)
        )  # Electricity consumption of centrifuge [kWh]
        m_output = 1.5 * prod

        process_name = "belt_filter"

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"recyc_water_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                elec_belt,
                recyc_water,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Rotary dryer
class rotary_dryer :
    def execute(self, prod, site_parameters, m_in) :
        E_dry = (0.3 * prod * 7) / heat_loss  # Thermal energy demand [MJ]
        elec_dry = 1 * prod * 0.3  # Electricity demand [kWh]
        m_output = prod

        process_name = "df_rotary_dryer"

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"E_{process_name}",
                f"elec_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                E_dry,
                elec_dry,
                ],
            }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Water purification
class water_purification :
    def execute(self, site_parameters, water) :
        waste = water * 0.25
        water_new = water * 0.25
        elec_purification = (2.783 * water / 1000)
        m_output = water

        process_name = "purification"

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"water_{process_name}",
                f"waste_{process_name}",
                f"elec_purification_{process_name}",
                ],
            "Values" : [
                m_output,
                water,
                waste,
                elec_purification,
                ],
            }

        df_process = pd.DataFrame(df_data)

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name' : process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None
            }


# Set up of the site - brine volumes and Li2CO3 production

def setup_site(eff, site_parameters) :
    vec_end = site_parameters['vec_end']  # vector of concentrations at the beginning of the process sequence
    Li_conc = vec_end[0]  # concentration of lithium in the brine

    Dens_ini = site_parameters['density_brine']  # initial density of brine
    v_pumpbrs = site_parameters['Brine_vol']  # volume of brine pumped per second
    op_days = site_parameters['operating_days']  # number of operating days per year
    if eff == site_parameters['Li_efficiency'] :
        eff = site_parameters['Li_efficiency']
    else:
        eff = eff   # efficiency of lithium extraction
    print(Li_conc)
    print(eff)

    # Mass of brine going into the process sequence
    v_pumpbr = ((v_pumpbrs / 1000) * op_days * 60 * 60 * 24) / eff  # volume of brine [m3/yr]
    m_pumpbr = v_pumpbr * Dens_ini * 1000  # mass of pumped brine per year [kg/yr]
    prod_year = ((v_pumpbrs / 1000) * op_days * 24 * 60 * 60 * (1000 * Dens_ini) * (Li_conc / 100)) / (
            (2 * Li) / (2 * Li + C + O * 3))

    return prod_year, m_pumpbr


def setup_logging(filename) :
    print(filename)
    # Define your fixed directory
    directory = "C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\data\\logging_files"
    # Ensure directory exists, if not, create it
    os.makedirs(directory, exist_ok=True)

    # Get the current timestamp in the format YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Split the filename and its extension
    base_filename, file_extension = os.path.splitext(filename)

    # Append the timestamp to the filename
    log_filename = f"{base_filename}_{timestamp}{file_extension}"

    # Join directory with filename to get the full path
    log_file_path = os.path.join(directory, log_filename)

    # Setup basic logging to only write logs to the file
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# ProcessManager class
class ProcessManager :
    def __init__(self, site_parameters, m_in, prod_initial, process_sequence, filename):
        setup_logging(filename)
        self.site_parameters = site_parameters
        self.data_frames = {}
        self.m_in = m_in
        self.prod = prod_initial
        self.dynamic_attributes = {}
        self.process_sequence = process_sequence
        self.process_dependencies = {
            'CaMg_removal_sodiumhydrox': ['MnZn_removal_lime'],
            'Liprec_BG': ['dissolution']
        }
        self.keys_not_to_overwrite = ["Ca_mass_brine", "water_RO", "water_evap"]
        self.logger = logging.getLogger('ProcessManager')
        self.log_folder = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/data/logging_files"

    def _get_args_for_process(self, process_instance) :
        process_type = type(process_instance)

        if process_type == SiFe_removal_limestone :
            return (self.site_parameters, self.m_in)
        elif process_type == MnZn_removal_lime :
            return (self.site_parameters, self.m_in)
        elif process_type == acidification :
            return (self.site_parameters, self.m_in)
        elif process_type == Li_adsorption :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == CaMg_removal_sodiumhydrox :
            return (self.dynamic_attributes["Ca_mass_brine"], self.site_parameters, self.m_in)
        elif process_type == ion_exchange_L :
            return (self.site_parameters, self.m_in)
        elif process_type == ion_exchange_H :
            return (self.site_parameters, self.m_in)
        elif process_type == reverse_osmosis :
            return (self.site_parameters, self.m_in)
        elif process_type == triple_evaporator :
            return (self.site_parameters, self.m_in)
        elif process_type == Liprec_TG :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == dissolution :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == Liprec_BG :
            return (self.dynamic_attributes["mass_CO2"], self.dynamic_attributes["prod_libicarb"], self.prod,
                    self.site_parameters, self.m_in)
        elif process_type == washing_TG :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == washing_BG :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == centrifuge_TG :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == centrifuge_BG :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == centrifuge_wash :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == belt_filter :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == rotary_dryer :
            return (self.prod, self.site_parameters, self.m_in)
        else :
            raise ValueError(f"Unsupported process: {process_type}")


    def run(self, filename):
        setup_logging(filename)
        print(filename)

        results = {}
        executed_processes = set()

        for process_instance in self.process_sequence:
            process_name = type(process_instance).__name__

            updated_args = self._get_args_for_process(process_instance)
            self.logger.info(f"Arguments for {process_name}: {updated_args}")

            if process_name in self.process_dependencies:
                for dependency in self.process_dependencies[process_name]:
                    if dependency not in executed_processes:
                        raise Exception(f"Dependency {dependency} for {process_name} has not been executed yet!")

            try:
                logging.info(f"Executing {process_name}")
                #print(f"Before process {process_name}, m_in = {self.m_in}")

                result = process_instance.execute(*updated_args)  # Unpack the updated_args
                #logging.info(f"Result for {process_name}: {result}")

                # Log the dataframes (results) after the process has been executed
                if 'data_frame' in result :
                    self.logger.info(f"Dataframe for {process_name}: {result['data_frame']}")

                for key, value in result.items() :
                    if key != 'm_out' and key != 'data_frame' :
                        # If the key is in keys_not_to_overwrite, handle its special logic
                        if key in self.keys_not_to_overwrite :
                            # If key already has a non-None value in dynamic_attributes, skip
                            if self.dynamic_attributes.get(value) is not None :
                                #logging.info(f"Skipped overwriting {key} because it already has a value")
                                continue
                            # If the new value is None, skip
                            elif value is None :
                                #logging.info(f"Skipped overwriting {key} with None")
                                continue
                        #logging.info(f"Setting {key} with value {value}")
                        self.dynamic_attributes[key] = value


                self.m_in = result['m_out']
                results[process_name] = result['data_frame']
                self.data_frames[result['process_name']] = result['data_frame']

                executed_processes.add(process_name)

            except Exception as e:
                logging.error(f"Error in {process_name}: {str(e)}")
                raise e


        if 'df_Li_adsorption' in self.data_frames and (
                'df_reverse_osmosis' in self.data_frames and 'df_triple_evaporator' in self.data_frames) :
            self.data_frames['df_Li_adsorption'], self.data_frames['df_reverse_osmosis'], self.data_frames[
                'df_triple_evaporator'] = Li_adsorption.update_adsorption(
                self.data_frames['df_Li_adsorption'],
                self.dynamic_attributes["water_RO"],
                self.dynamic_attributes['water_evap'],
                self.data_frames['df_reverse_osmosis'],
                self.data_frames['df_triple_evaporator'],
                T_desorp,
                hCHH,
                heat_loss,
                self.site_parameters
                )

        return results

    def calculate_resource_per_prod_mass(self, result_df, prod) :
        energy_sum = 0
        elec_sum = 0
        water_sum = 0
        production_mass = prod

        for df_name, df in self.data_frames.items() :
            # Summing resources
            energy_sum += df[df['Variables'].str.startswith('E_')]['Values'].sum()
            elec_sum += df[df['Variables'].str.startswith('elec_')]['Values'].sum()
            water_sum += df[df['Variables'].str.startswith('water_')]['Values'].sum()

        if production_mass > 0 :
            energy_per_prod_mass = energy_sum / production_mass
            elec_per_prod_mass = elec_sum / production_mass
            water_per_prod_mass = water_sum / production_mass
        else :
            energy_per_prod_mass = elec_per_prod_mass = water_per_prod_mass = None

        return energy_per_prod_mass, elec_per_prod_mass, water_per_prod_mass






