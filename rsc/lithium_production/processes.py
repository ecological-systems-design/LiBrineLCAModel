from rsc.lithium_production.chemical_formulas import *

from rsc.lithium_production.operational_data_salton import *

import pandas as pd
import os

if not os.path.exists("../../images") :
    os.mkdir("../../images")

# Operational data input
op_data = pd.ExcelFile(r'C:\Users\Schenker\PycharmProjects\pythonProject\data\data_extractionsites.xlsx')
data = op_data.parse("Sheet1")

locations = [("Salton Sea", "Sal"), ("Upper Rhine Valley", "URG")]

prod = data['Salton Sea'][0]  # Production of lithium carbonate [kg/yr]
op_days = data['Salton Sea'][1]  # Operational days per year
life = data['Salton Sea'][2]  # Expected time of mining activity [yr]
v_pumpbrs = data['Salton Sea'][3]  # Brine pumped to the surface [L/s]
v_pumpfrw = data['Salton Sea'][4]  # Fresh water pumped to the surface at evaporation ponds [L/s]
eff = data['Salton Sea'][13]  # Overall Li efficiency
elev = data['Salton Sea'][15]  # Elevation of mine site
boil_point = data['Salton Sea'][16]  # Boiling point at processing plant [°C]
T_out = data['Salton Sea'][17]  # Annual air temperature [°C]
Dens_ini = data['Salton Sea'][18]  # Density of initial brine [g/cm3]

vec_end = [0 for _ in range(15)]
for i in range(0, 14) :
    vec_end[i] = data['Salton Sea'][i + 19]

sum_end = sum(vec_end)

deion_water = []
energy = []
electricity = []
production = []

# Geothermal energy
v_pumpbr = ((v_pumpbrs / 1000) * op_days * 60 * 60 * 24) / eff  # volume of brine [m3/yr]
m_pumpbr = v_pumpbr * Dens_ini * 1000  # mass of pumped brine per year [kg/yr]
prod_year = ((v_pumpbrs / 1000) * op_days * 24 * 60 * 60 * (1000 * Dens_ini) * (vec_end[0] / 100)) / (
        (2 * Li) / (2 * Li + C + O * 3))

m_out = m_pumpbr

Li_out_RO = 5000
Li_in_RO = 2500
Li_out_evaporator = 30000

name_list = ['df_SiFe_removal_limestone', 'df_MnZn_removal_lime', 'df_acidification', 'df_Li_adsorption',
                 'df_CaMg_removal_sodiumhydrox', 'df_ion_exchange_L', 'df_reverse_osmosis', 'df_triple_evaporator',
                 'df_Liprec_TG', 'df_centrifuge_TG', 'df_washing_TG', 'df_dissolution', 'df_Liprec_BG',
                 'df_centrifuge_BG',
                 'df_washing_BG', 'df_centrifuge_wash', 'df_rotary'
                 ]


# Si & Fe removal by precipitation
def proc_SiFe_removal_limestone(m_in=m_out) :
    process_name = 'df_SiFe_removal_limestone'
    E_SiFe = 0
    energy.append(E_SiFe)
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

    df_SiFe_removal_limestone = pd.DataFrame(df_data)
    df_SiFe_removal_limestone['per kg'] = df_SiFe_removal_limestone['Values'] / df_SiFe_removal_limestone.iloc[0][1]

    print(df_SiFe_removal_limestone)
    m_out = df_SiFe_removal_limestone.iloc[-1]['Values']
    return m_out, df_SiFe_removal_limestone


# Mn and Zn removal by precipitation
def proc_MnZn_removal_lime(m_in=m_out) :
    process_name = 'df_MnZn_removal_lime'
    E_MnZn = 0  # Heating necessary?
    energy.append(E_MnZn)

    Mn_mass = vec_end[-6] / 100 * m_in
    Zn_mass = vec_end[-4] / 100 * m_in

    lime_MnZn = (Mn_mass / Mn + Zn_mass / Zn) * (Ca + 2 * (O + H)) * 1.2
    water_lime = (lime_MnZn / (Ca + O)) * (H * 2 + O)

    deion_water.append(water_lime)

    waste_Mn = -(Mn_mass / Mn * (Mn + 2 * (O + H)))
    waste_Zn = -(Zn_mass / Zn * (Zn + 2 * (O + H)))
    waste_sum = waste_Mn + waste_Zn

    Ca_mass_brine = Ca / (Ca + C + 3 * O) * lime_MnZn  # Calculating mass of Ca in brine # dH calculating
    m_output = m_in + waste_Mn + waste_Zn + Ca_mass_brine + lime_MnZn + water_lime

    df_data = {
        'Variables' : [f'm_output_{process_name}', f'm_in_{process_name}', f'E_{process_name}', f'chemical_lime_{process_name}',
                       f'water_{process_name}', f'waste_solid_{process_name}',
                       f'Ca_mass_{process_name}'],
        'Values' : [m_output, m_in, E_MnZn, lime_MnZn, water_lime, waste_sum, Ca_mass_brine]
        }

    df_MnZn_removal_lime = pd.DataFrame(df_data)
    df_MnZn_removal_lime['per kg'] = df_MnZn_removal_lime['Values'] / df_MnZn_removal_lime.iloc[0][1]
    print(df_MnZn_removal_lime)

    m_out = df_MnZn_removal_lime.iloc[-1]['Values']

    return m_out, df_MnZn_removal_lime, Ca_mass_brine


# acidification & ion exchanger, T = 30 - 100 °C, pH adaption
def proc_acidification(m_in=m_out) :
    process_name =  'df_acidification'

    # pH adaption
    pH_ini = 8  # Initial pH of concentrated brine
    pOH_ini = 14 - pH_ini  # Initial pOH of concentrated brine
    pH_aft = 4.5  # End pH of concentrated brine by adding HCl solution
    pOH_aft = 14 - pH_aft  # End pOH of concentrated brine by adding HCl solution

    delta_H_conc = (10 ** -pH_aft) - (10 ** -pH_ini)  # Difference of number of H+ in brine
    delta_OH_conc = (10 ** -pOH_ini) - (10 ** -pOH_aft)  # Difference of number OH- in brine

    HCl_pH = ((((delta_H_conc * (m_in / (1000 * Dens_ini)) * (H + Cl) + delta_OH_conc * (m_in / (Dens_ini * 1000)) * (
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

    df_acidification = pd.DataFrame(df_data)
    df_acidification['per kg'] = df_acidification['Values'] / df_acidification.iloc[0][1]

    m_out = df_acidification.iloc[-1]['Values']
    print(df_acidification)

    return m_out, df_acidification


# Li-ion selective adsorption
def proc_Li_adsorption(m_in=m_out) :
    process_name = 'df_Li_adsorption'
    T_adsorp = 85
    adsorp_capacity = 0.008
    adsorbent_loss = prod * ((2 * Li) / (2 * Li + C + 3 * O)) * 1.25
    adsorbent_invest = prod * ((2 * Li) / (2 * Li + C + 3 * O)) / adsorp_capacity
    adsorbent = (adsorbent_invest / life) + adsorbent_loss
    water_adsorbent = 100 * adsorbent_invest
    deion_water.append(water_adsorbent)
    elec_adsorp = 0.73873739 * 10 ** (-3) * (
            m_in + water_adsorbent
    )  # Electricity demand for ion exchanger [kWh]
    electricity.append(elec_adsorp)
    E_adsorp = (
                       ((T_adsorp - T_out) * hCHH * water_adsorbent) / 10 ** 6
               ) / heat_loss
    energy.append(E_adsorp)

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

    df_Li_adsorption = pd.DataFrame(df_data)
    df_Li_adsorption["per kg"] = df_Li_adsorption["Values"] / df_Li_adsorption.iloc[0][1]
    print(df_Li_adsorption)

    m_out = df_Li_adsorption.iloc[0]["Values"]

    return m_out, df_Li_adsorption


def proc_CaMg_removal_sodiumhydrox(Ca_mass_leftover, m_in=m_out) :
    process_name = 'df_CaMg_removal_sodiumhydrox'
    left_over = 0.0002
    Ca_mass = left_over * (vec_end[4] / 100 * m_in + Ca_mass_leftover)
    Mg_mass = left_over * vec_end[5] / 100 * m_in
    Ba_mass = left_over * vec_end[-1] / 100 * m_in
    Sr_mass = left_over * vec_end[-3] / 100 * m_in

    NaOH = (Mg_mass / Mg + Ba_mass / Ba + Sr_mass / Sr) * 2 * (Na + O + H) * 1.2
    water_NaOH = NaOH / (Na + O + H) * (2 * H + O) * 1.2  # with process water
    deion_water.append(water_NaOH)

    sodaash_Ca = Ca_mass / Ca * (2 * Na + C + 3 * O)
    water_sodaash_Ca = sodaash_Ca / 0.25  # with process water
    water_sum = water_sodaash_Ca + water_NaOH
    deion_water.append(water_sodaash_Ca)

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

    df_CaMg_removal_sodiumhydrox = pd.DataFrame(df_data)
    df_CaMg_removal_sodiumhydrox["per kg"] = df_CaMg_removal_sodiumhydrox["Values"] / \
                                             df_CaMg_removal_sodiumhydrox.iloc[0][1]

    m_out = df_CaMg_removal_sodiumhydrox.iloc[0]["Values"]
    print(df_CaMg_removal_sodiumhydrox)

    return m_out, df_CaMg_removal_sodiumhydrox


def proc_Mg_removal_soda(m_in=m_out) :
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
    water_soda_Mg = (sodaash_Mg) / 0.25
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

    df_Mg_removal_soda = pd.DataFrame(df_data)
    df_Mg_removal_soda["per kg"] = df_Mg_removal_soda["Values"] / df_Mg_removal_soda.iloc[0][1]

    m_out = df_Mg_removal_soda.iloc[0]["Values"]

    return m_out, df_Mg_removal_soda


def proc_Mg_removal_quick(m_in=m_out) :
    process_name = "Mg_removal_quick"

    Mg_lime_ini = 0.05  # in wt. % of the pulp
    lime_high = (((Mg_lime_ini / 100) * m_in) / Mg) * (Ca + O * 2 + H * 2) * 1.2
    water_lime_high = (lime_high / (Ca + O)) * (H * 2 + O)
    deion_water.append(water_lime_high)

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

    df_Mg_removal_quick = pd.DataFrame(df_data)
    df_Mg_removal_quick["per kg"] = df_Mg_removal_quick["Values"] / df_Mg_removal_quick.iloc[0][1]

    m_out = df_Mg_removal_quick.iloc[0]["Values"]

    return m_out, df_Mg_removal_quick


def proc_ion_exchange_L(m_in=m_out) :
    process_name =  'df_ion_exchange_L'

    elec_IX = 0.82 * 10 ** (-3) * m_in  # Electricity demand for ion exchanger [kWh]
    electricity.append(elec_IX)
    water_IX = 1.1 * m_in  # Required mass of deionized water [kg]
    deion_water.append(water_IX)
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

    df_ion_exchange_L = pd.DataFrame(df_data)
    df_ion_exchange_L["per kg"] = df_ion_exchange_L["Values"] / df_ion_exchange_L.iloc[0][1]

    m_out = df_ion_exchange_L.iloc[0]["Values"]

    return m_out, df_ion_exchange_L


def proc_ion_exchang_H(m_in=m_out) :
    process_name = "ion_exchange_H"

    elec_IX = 3 * 0.82 * 10 ** (-3) * m_in  # Electricity demand for ion exchanger [kWh]
    electricity.append(elec_IX)
    water_IX = 3 * 0.5 * (2 * m_in)  # Required mass of deionized water [kg]
    deion_water.append(water_IX)
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

    df_ion_exchange_H = pd.DataFrame(df_data)
    df_ion_exchange_H["per kg"] = df_ion_exchange_H["Values"] / df_ion_exchange_H.iloc[0][1]

    m_out = df_ion_exchange_H.iloc[0]["Values"]

    return m_out, df_ion_exchange_H


def proc_reverse_osmosis(m_in=m_out) :
    process_name = 'df_reverse_osmosis'

    elec_osmosis = (2.783 * m_in / 1000)  # kWh, based on ecoinvent (2008)
    electricity.append(elec_osmosis)
    water_RO = (1 - (Li_in_RO / Li_out_RO)) * m_in
    m_output = Li_in_RO / Li_out_RO * m_in

    df_data = {
        "Variables" : [
            f"m_output_{process_name}",
            f"m_in_{process_name}",
            f"elec_{process_name}",
            f"water_{process_name}",
            ],
        "Values" : [
            m_output,
            m_in,
            elec_osmosis,
            water_RO,
            ],
        }

    df_reverse_osmosis = pd.DataFrame(df_data)
    df_reverse_osmosis["per kg"] = df_reverse_osmosis["Values"] / df_reverse_osmosis.iloc[0][1]

    m_out = df_reverse_osmosis.iloc[0]["Values"]

    return m_out, df_reverse_osmosis, water_RO


def proc_triple_evaporator(m_in=m_out) :
    process_name =  'df_triple_evaporator'

    E_evap = m_in / 1100 * 145  # MJ per m3 input
    energy.append(E_evap)
    elec_evap = m_in / 1100 * 2  # kWh per m3 input
    electricity.append(elec_evap)
    placer = Li_out_RO / Li_out_evaporator * m_in
    steam = placer / 16  # taking from geothermal power plant
    water_evap = (1 - Li_out_RO / Li_out_evaporator) * m_in
    m_output = Li_out_RO / Li_out_evaporator * m_in

    df_data = {
        "Variables" : [
            f"m_output_{process_name}",
            f"m_in_{process_name}",
            f"E_{process_name}",
            f"elec_{process_name}",
            f"steam_{process_name}",
            f"water_{process_name}",
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

    df_triple_evaporator = pd.DataFrame(df_data)
    df_triple_evaporator["per kg"] = df_triple_evaporator["Values"] / df_triple_evaporator.iloc[0][1]

    m_out = df_triple_evaporator.iloc[0]["Values"]

    return m_out, df_triple_evaporator, water_evap


def proc_Liprec_TG(m_in=m_out) :
    process_name =  'df_Liprec_TG'

    E_Liprec = (((T_Liprec - T_out) * hCHH_bri * m_in) /
                10 ** 6) / heat_loss  # Thermal energy demand [MJ]
    energy.append(E_Liprec)
    sodaash_Liprec = ((prod * 1000 / (Li * 2 + C + O * 3)) * (Na * 2 + C + O * 3) /
                      1000) / 0.7  # stoichiometrically calculated soda ash demand [kg]
    prod_NaCl2 = (prod * 1000 / (Li * 2 + C + O * 3)) * (Na + Cl) / 1000  # waste production [kg]
    water_sodaash = sodaash_Liprec / 0.2  # water demand to produce 20 vol. % Na2CO3 solution [kg]
    deion_water.append(water_sodaash)
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

    df_Liprec_TG = pd.DataFrame(df_data)
    df_Liprec_TG["per kg"] = df_Liprec_TG["Values"] / df_Liprec_TG.iloc[0][1]

    m_out = df_Liprec_TG.iloc[0]["Values"]

    return m_out, df_Liprec_TG


def proc_dissolution(m_in=m_out) :
    process_name = "df_dissolution"

    prod_libicarb = prod / (Li * 2 + C + O * 3) * (
            2 * (Li + H + C + O * 3))  # mass of lithiumbicarbonate [kg]
    mass_HCO = prod_libicarb * (H * 2 + C + O * 3) / (
            Li + H + C + O * 3)  # mass of required HCO3- in solution [kg]
    mass_CO2 = (
                       ((C + O * 2) / (H * 2 + C + O * 3)) * mass_HCO
               ) * 0.6  # mass of required CO2 to dissolve lithium carbonate [kg]
    water_deion2 = (prod / 0.052)  # - (prod * 2)  # Required mass of deionized water to dissolve lithium carbonate [kg]
    elec_dissol = 0
    electricity.append(elec_dissol)
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

    df_dissolution = pd.DataFrame(df_data)
    df_dissolution["per kg"] = df_dissolution["Values"] / df_dissolution.iloc[0][1]

    m_out = df_dissolution.iloc[0]["Values"]

    return m_out, df_dissolution, mass_CO2, prod_libicarb


def proc_Liprec_BG(mass_CO2, prod_libicarb, m_in=m_out) :
    process_name = 'df_Liprec_BG'
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
    energy.append(E_seclicarb)
    mass_h2o = -((
                         (H * 2 + O) / (2 * (Li + H + C + O * 3))
                 ) * prod_libicarb)  # Mass of H2O lost due to precipitation of Li2CO3 [kg]
    m_output = m_in + mass_h2o + prod - mass_CO2  # Output mass of this process [kg]

    df_data = {
        "Variables" : [
            f"m_output_{process_name}",
            f"m_in_{process_name}",
            f"waste_heat{process_name}",
            f"E_{process_name}"
            ],
        "Values" : [
            m_output,
            m_in,
            waste_heat_sum,
            E_seclicarb
            ],
        }

    df_Liprec_BG = pd.DataFrame(df_data)
    df_Liprec_BG["per kg"] = df_Liprec_BG["Values"] / df_Liprec_BG.iloc[0][1]

    m_out = df_Liprec_BG.iloc[0]["Values"]

    return m_out, df_Liprec_BG


# Washing Li2CO3 (TG)
def proc_washing_TG(m_in=m_out) :
    T_op = T_out
    m_in_wash = m_in
    water_deion = 2 * prod  # Mass of water required for washing [kg]
    deion_water.append(water_deion)
    E_deion = (((boil_point - T_op) * hCHH * water_deion) / 10 ** 6) / heat_loss  # Thermal energy demand [MJ]
    energy.append(E_deion)
    m_output = 3.5 * prod  # Mass output of this process [kg]

    function_name = 'df_washing_TG'

    df_data = {
        "Variables" : [f"m_output_{function_name}", f"m_in_{function_name}", f"water_{function_name}",
                       f"E_{function_name}"],
        "Values" : [m_output, m_in_wash, water_deion, E_deion],
        }

    df_washing_TG = pd.DataFrame(df_data)
    df_washing_TG[f"per kg"] = df_washing_TG["Values"] / df_washing_TG.iloc[0]["Values"]

    m_out = df_washing_TG.iloc[0]["Values"]

    return m_out, df_washing_TG


# Washing Li2CO3 (BG)
def proc_washing_BG(m_in=m_out) :
    m_in_wash = m_in
    T_op = T_out
    water_deion = 2 * prod  # Mass of water required for washing [kg]
    deion_water.append(water_deion)
    E_deion = (((boil_point - T_op) * hCHH * water_deion) / 10 ** 6) / heat_loss  # Thermal energy demand [MJ]
    energy.append(E_deion)
    m_output = 3.5 * prod  # Mass output of this process [kg]

    process_name = 'df_washing_BG'

    df_data = {
        "Variables" : [f"m_output_{process_name}", f"m_in_{process_name}", f"water_{process_name}",
                       f"E_{process_name}"],
        "Values" : [m_output, m_in_wash, water_deion, E_deion],
        }

    df_washing_BG = pd.DataFrame(df_data)
    df_washing_BG[f"per kg"] = df_washing_BG["Values"] / df_washing_BG.iloc[0]["Values"]

    m_out = df_washing_BG.iloc[0]["Values"]

    return m_out, df_washing_BG


# Centrifuge after TG
def proc_centrifuge_TG(m_in=m_out) :
    elec_centri = 1.3 * m_in / (Dens_ini * 1000)  # Electricity consumption of centrifuge [kWh]
    electricity.append(elec_centri)
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

    df_centrifuge_TG = pd.DataFrame(df_data)
    df_centrifuge_TG["per kg"] = df_centrifuge_TG["Values"] / df_centrifuge_TG.iloc[0]["Values"]

    m_out = df_centrifuge_TG.iloc[0]["Values"]

    return m_out, df_centrifuge_TG


# Centrifuge after BG
def proc_centrifuge_BG(m_in=m_out) :
    elec_centri = 1.3 * m_in / (Dens_ini * 1000)  # Electricity consumption of centrifuge [kWh]
    electricity.append(elec_centri)
    waste_centri = -((m_in - 1.5 * prod) / 1000)
    m_output = 1.5 * prod

    process_name =  'df_centrifuge_BG'

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

    df_centrifuge_BG = pd.DataFrame(df_data)
    df_centrifuge_BG["per kg"] = df_centrifuge_BG["Values"] / df_centrifuge_BG.iloc[0]["Values"]

    m_out = df_centrifuge_BG.iloc[0]["Values"]

    return m_out, df_centrifuge_BG


# Centrifuge after washing
def proc_centrifuge_wash(m_in=m_out) :
    elec_centri = 1.3 * m_in / (Dens_ini * 1000)  # Electricity consumption of centrifuge [kWh]
    electricity.append(elec_centri)
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

    df_centrifuge_wash = pd.DataFrame(df_data)
    df_centrifuge_wash["per kg"] = df_centrifuge_wash["Values"] / df_centrifuge_wash.iloc[0]["Values"]

    m_out = df_centrifuge_wash.iloc[0]["Values"]

    return m_out, df_centrifuge_wash


# Belt filter
def proc_belt_filter(m_in=m_out) :
    recyc_water = m_in - 1.5 * prod  # No waste is produced because the residual is sent back
    elec_belt = 0.4 * (
            ((m_in - 1.5 * prod) / dens_H2O) + (1.5 * prod / dens_Licarb)
    )  # Electricity consumption of centrifuge [kWh]
    electricity.append(elec_belt)
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

    df_belt = pd.DataFrame(df_data)
    df_belt["per kg"] = df_belt["Values"] / df_belt.iloc[0]["Values"]

    m_out = df_belt.iloc[0]["Values"]

    return m_out, df_belt


# Rotary dryer
def proc_rot_dry(m_in=m_out) :
    E_dry = (0.3 * prod * 7) / heat_loss  # Thermal energy demand [MJ]
    energy.append(E_dry)
    elec_dry = 1 * prod * 0.3  # Electricity demand [kWh]
    electricity.append(elec_dry)
    m_output = prod

    process_name = "df_rotary"

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

    df_rotary = pd.DataFrame(df_data)
    df_rotary["per kg"] = df_rotary["Values"] / df_rotary.iloc[0]["Values"]

    m_out = df_rotary.iloc[0]["Values"]

    return m_out, df_rotary


# Water purification
def proc_purification(water=sum(deion_water)) :
    waste = water * 0.25
    water_new = water * 0.25
    elec_purification = (2.783 * water / 1000)
    electricity.append(elec_purification)
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

    df_purification = pd.DataFrame(df_data)

    m_out = df_purification.iloc[0]["Values"]

    return m_out, df_purification


location = "Salton Sea"
abbrev_loc = "Sal"


def loop_functions(eff, Li_conc, op_location=location, abbrev_loc=abbrev_loc):
    # Extract data

    ini_data = extract_data(op_location, abbrev_loc, Li_conc=Li_conc)
    print(ini_data)

    prod = ini_data[abbrev_loc]["production"]  # Production of lithium carbonate [kg/yr]
    op_days = ini_data[abbrev_loc]["operation_days"]  # Operational days per year
    life = ini_data[abbrev_loc]["lifetime"]  # Expected time of mining activity [yr]
    v_pumpbrs = ini_data[abbrev_loc]["Brine_vol"]  # Brine pumped to the surface [L/s]
    v_pumpfrw = ini_data[abbrev_loc]["Freshwater_vol"]  # Fresh water pumped to the surface at evaporation ponds [L/s]
    eff = ini_data[abbrev_loc]["Li_efficiency"]  # Overall Li efficiency
    elev = ini_data[abbrev_loc]["elevation" ]  # Elevation of mine site
    boil_point = ini_data[abbrev_loc]["boilingpoint_process"]  # Boiling point at processing plant [°C]
    T_out = ini_data[abbrev_loc]["annual_airtemp"]  # Annual air temperature [°C]
    Dens_ini = ini_data[abbrev_loc]["density_brine"]  # Density of initial brine [g/cm3]

    vec_end = ini_data[abbrev_loc]['vec_end']
    Li_conc = vec_end[0]


    # Geothermal energy
    v_pumpbr = ((v_pumpbrs / 1000) * op_days * 60 * 60 * 24) / eff  # volume of brine [m3/yr]
    m_pumpbr = v_pumpbr * Dens_ini * 1000  # mass of pumped brine per year [kg/yr]
    prod_year = ((v_pumpbrs / 1000) * op_days * 24 * 60 * 60 * (1000 * Dens_ini) * (Li_conc / 100)) / (
            (2 * Li) / (2 * Li + C + O * 3))

    # Required processes
    prod = prod_year
    print(prod_year)

    # Initialize lists to store the sums
    process_name = []
    water_sums = []
    elec_sums = []
    E_sums = []

    # Initialize an initial input value
    m_in = m_pumpbr
    print(m_pumpbr)

    m_out, df_SiFe_removal_limestone = proc_SiFe_removal_limestone(m_in=m_pumpbr)
    m_out, df_MnZn_removal_lime, Ca_mass_brine = proc_MnZn_removal_lime(m_in=df_SiFe_removal_limestone.iloc[0, 1])
    m_out, df_acidification = proc_acidification(m_in=df_MnZn_removal_lime.iloc[0, 1])
    m_out, df_adsorption = proc_Li_adsorption(m_in=df_acidification.iloc[0, 1])
    m_out, df_CaMg_removal_sodiumhydrox = proc_CaMg_removal_sodiumhydrox(Ca_mass_leftover=Ca_mass_brine,
                                                                         m_in=df_adsorption.iloc[0, 1])
    m_out, df_ion_exchange_L = proc_ion_exchange_L(m_in=df_CaMg_removal_sodiumhydrox.iloc[0, 1])
    m_out, df_reverse_osmosis, water_RO = proc_reverse_osmosis(m_in=df_ion_exchange_L.iloc[0, 1])
    m_out, df_triple_evaporator, water_evap = proc_triple_evaporator(m_in=df_reverse_osmosis.iloc[0, 1])
    m_out, df_Liprec_TG = proc_Liprec_TG(m_in=df_triple_evaporator.iloc[0, 1])
    m_out, df_washing_TG = proc_washing_TG(m_in=df_Liprec_TG.iloc[0, 1])
    m_out, df_centrifuge_TG = proc_centrifuge_TG(m_in=df_washing_TG.iloc[0, 1])
    m_out, df_dissolution, mass_CO2, prod_libicarb = proc_dissolution(m_in=df_centrifuge_TG.iloc[0, 1])
    m_out, df_Liprec_BG = proc_Liprec_BG(mass_CO2, prod_libicarb, m_in=df_dissolution.iloc[0, 1])
    m_out, df_centrifuge_BG = proc_centrifuge_BG(m_in=df_Liprec_BG.iloc[0, 1])
    m_out, df_washing_BG = proc_washing_BG(m_in=df_centrifuge_BG.iloc[0, 1])
    m_out, df_centrifuge_wash = proc_centrifuge_wash(m_in=df_washing_BG.iloc[0, 1])
    m_out, df_rotary = proc_rot_dry(m_in=df_centrifuge_wash.iloc[0, 1])

    new_value = df_adsorption.iloc[3, 1] - water_RO - water_evap

    df_adsorption.loc[3, 'Values'] = new_value

    new_value_kg = df_adsorption.iloc[3, 2] - (water_RO / df_adsorption.iloc[0, 1]) - (
            water_evap / df_adsorption.iloc[0, 1])

    df_adsorption.loc[3, 'per kg'] = new_value_kg

    backflow_ro = df_reverse_osmosis.iloc[0, 1] - df_reverse_osmosis.iloc[2, 1]

    df_reverse_osmosis.loc[len(df_reverse_osmosis.index)] = ['backflow_ro', backflow_ro, 0]

    backflow_evap = df_triple_evaporator.iloc[0, 1] - df_triple_evaporator.iloc[4, 1]

    df_triple_evaporator.loc[len(df_triple_evaporator.index)] = ['backflow_evap', backflow_evap, 0]

    E_adsorp_adapted = (((T_desorp - T_out) * hCHH * df_adsorption.iloc[3, 1]) / 10 ** 6) / heat_loss

    df_adsorption.loc[5, 'Values'] = E_adsorp_adapted

    # energy[2] = E_adsorp_adapted

    df_adsorption.loc[5, 'per kg'] = E_adsorp_adapted / df_adsorption.iloc[0, 1]

    df_reverse_osmosis_ad = df_reverse_osmosis.drop(3)
    df_triple_evaporator_ad = df_triple_evaporator.drop(5)
    df_centrifuge_TG_ad = df_centrifuge_TG.drop(3)

    df_list = [
        df_SiFe_removal_limestone, df_MnZn_removal_lime, df_acidification, df_adsorption,
        df_CaMg_removal_sodiumhydrox, df_ion_exchange_L, df_reverse_osmosis_ad, df_triple_evaporator_ad,
        df_Liprec_TG, df_centrifuge_TG_ad, df_washing_TG, df_dissolution, df_Liprec_BG, df_centrifuge_BG,
        df_washing_BG, df_centrifuge_wash, df_rotary
        ]

    # Iterate through each step and calculate the sums
    for process_df in df_list :
        water_sums.append(process_df[process_df['Variables'].str.contains('water')]['Values'].sum())
        elec_sums.append(process_df[process_df['Variables'].str.contains('elec')]['Values'].sum())
        E_sums.append(process_df[process_df['Variables'].str.contains('E_')]['Values'].sum())

    # Create a DataFrame to display the sums for each step
    summary_df = pd.DataFrame({
        'Water Sum' : water_sums,
        'Elec Sum' : elec_sums,
        'E_ Sum' : E_sums
        })

    # Calculate the sums for each column
    water_sum_total = sum(water_sums) / prod
    elec_sum_total = sum(elec_sums) / prod
    E_sum_total = sum(E_sums) / prod

    summary_tot_df = pd.DataFrame({
        'Water Sum per prod' : [water_sum_total],
        'Elec Sum per prod' : [elec_sum_total],
        'E_ Sum per prod' : [E_sum_total]
        })

    return df_list, summary_df, summary_tot_df





