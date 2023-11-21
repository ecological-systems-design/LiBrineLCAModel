from rsc.lithium_production.chemical_formulas import *

from rsc.lithium_production.import_site_parameters import *

from rsc.Postprocessing_results.visualization_functions import Visualization

import pandas as pd
import os
import logging
import inspect
import json
import datetime
import numpy as np
import pickle
import math

if not os.path.exists("../../results") :
    os.mkdir("../../results")

# Evaporation ponds
class evaporation_ponds :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_evaporation_ponds'
        op_days = site_parameters['operating_days']  # Operational days per year
        vec_ini = site_parameters['vec_ini']  # vector of chemical composition of initial brine
        vec_end = site_parameters['vec_end']  # vector of chemical composition of enriched brine sent to processing plant
        density_initial_brine = site_parameters['density_brine']  # density of initial brine
        density_enriched_brine = site_parameters['density_enriched_brine']  # density of enriched brine
        evaporation_rate = site_parameters['evaporation_rate'] # evaporation rate of brine in evaporation ponds
        quicklime_reported = site_parameters['quicklime_reported']  # question if quicklime is used or not in the evaporation ponds
        freshwater_reported = site_parameters['freshwater_reported']    # question if freshwater is reported or not in the evaporation ponds
        freshwater_vol = site_parameters['freshwater_vol']  # volume of freshwater pumped to the surface at evaporation ponds [L/s]
        brine_vol = site_parameters['brine_vol']  # volume of brine pumped to the surface at evaporation ponds [L/s]
        overall_efficiency = site_parameters['Li_efficiency']  # overall efficiency
        second_Li_enrichment_reported = site_parameters['second_Li_enrichment_reported']  # question if second Li enrichment is reported or not in the evaporation ponds
        second_Li_enrichment = site_parameters['second_Li_enrichment']  # second Li enrichment, either 0 or reported value
        diesel_reported = site_parameters['diesel_reported']    # question if diesel is reported or not in the evaporation ponds
        depth_well_brine = site_parameters['well_depth_brine']  # depth of the well for brines
        depth_well_freshwater = site_parameters['well_depth_freshwater']  # depth of the well for freshwater
        life = site_parameters['lifetime']  # lifetime of the plant

        operating_time = op_days * 24 * 60 * 60  # Operating time in seconds

        # Volume and mass changes during evaporation
        brinemass_req = vec_end[0] / vec_ini[0]  # Required mass of brine to gain 1 kg concentrated brine with 6 wt. % Li
        brinemass_proc = 1.00
        brinemass_evap = brinemass_req - brinemass_proc  # Required mass which needs to be evaporated and precipitated


        # Elemental losses during evaporation based on chemical composition
        vec_loss = [
            (brinemass_req * (vec_ini[i] / 100) - (vec_end[i] / 100) * brinemass_proc)
            if not math.isnan(vec_ini[i]) and not math.isnan(vec_end[i])
            else float('nan')
            for i in range(len(vec_end))
            ]



        # Calculation of precipitated salts and brine sent to the processsing plant
        m_saltbrine_removed = brinemass_evap / brinemass_req * m_in
        # Sum only non-nan values in vec_loss
        total_loss = np.nansum(vec_loss)

        # Exclude the last element if it is nan in the total_loss calculation
        if not np.isnan(vec_loss[-1]) :
            total_loss_excluding_last = total_loss - vec_loss[-1]
        else :
            total_loss_excluding_last = total_loss

        m_salt = (total_loss_excluding_last / total_loss) * m_saltbrine_removed

        # Quicklime demand if reported
        if quicklime_reported == 1 :
            water_quicklime, chemical_quicklime, m_output, m_saltbrine2 = self.quicklime_usage(vec_loss, vec_end, m_saltbrine_removed, m_in,
                                                                                               brinemass_evap, second_Li_enrichment)

        else:
            water_quicklime = 0
            chemical_quicklime = 0
            pass

        # Freshwater demand if reported
        if freshwater_reported == 1 :
            water_pipewashing = (freshwater_vol / 1000) * dens_frw * operating_time # mass of fresh water pumped per year [kg/year], in evaporation ponds
            sulfuric_acid = sulfuricacid_solution * water_pipewashing

        else:
            water_pipewashing = self.freshwater_usage(proxy_freshwater_EP, m_saltbrine_removed, m_saltbrine2)
            sulfuric_acid = sulfuricacid_solution * water_pipewashing
            pass

        # Overall water demand in evaporation ponds
        water_evaporationponds = water_pipewashing + water_quicklime

        # Land use to produce 1 kg concentrated brine
        area_occup = brinemass_evap / 1000 / evaporation_rate
        transf = area_occup / life
        m_Li = m_in * vec_ini[0] / 100  # mass of lithium in the annual pumped brine [kg]

        # Well field system
        power_well = gravity_constant * (
                    density_initial_brine * brine_vol * depth_well_brine + freshwater_vol * depth_well_freshwater) / eff_pw  # Electricity for pumping activity of wells required for brine and fresh water [kWh]
        electric_well = power_well * 1.1 * (1 / (3600 * 1000)) * operating_time

        # Salt harvesting until processing plant
        if diesel_reported == 1 :
            hrs_excav = site_parameters['diesel_consumption']/37  # working hours for excavators
        else:
            hrs_excav = self.diesel_usage_proxy(proxy_harvest, m_saltbrine_removed)


        waste_water = water_pipewashing


        m_output = m_in - m_saltbrine_removed
        print(f'm_in: {m_in}')
        print(f'm_saltbrine: {m_saltbrine_removed}')
        print(f'evaporation_ponds: {m_output}')

        df_data = {
            'Variables' : [f'm_output_{process_name}',
                           f'm_Li_{process_name}',
                           f'elec_{process_name}',
                           f'diesel_machine_{process_name}',
                           f'water_{process_name}',
                           f'land_occupation_{process_name}',
                           f'land_transform_unknown_{process_name}',
                           f'land_transform_minesite_{process_name}',
                           f'chemical_lime_{process_name}',
                           f'chemical_sulfuricacid_{process_name}',
                           f'waste_salt_{process_name}',
                           f'waste_liquid_{process_name}'],
            'Values' : [m_output, m_Li, electric_well, hrs_excav, water_evaporationponds, area_occup, transf, transf,
                        chemical_quicklime, sulfuric_acid, (-m_salt), -waste_water]
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }

    def quicklime_usage(self, vec_loss, vec_end, m_saltbri, m_bri_proc, bri_evap, second_Li_enrichment) :
        """
           Calculate quicklime usage and related parameters.

           :param vec_loss: List of elemental losses during evaporation.
           :param vec_end: Vector of chemical composition of enriched brine.
           :param m_saltbri: Mass of salt in brine.
           :param m_bri_proc: Mass of concentrated brine sent to processing plant.
           :param bri_evap: Required mass which needs to be evaporated and precipitated.
           :param second_Li_enrichment: Second Li enrichment value.
           :return: Tuple of water lime low quality, lime low quality, output mass, and salt brine mass for second enrichment.
           """

        # First magnesium and calcium removal by adding low quality quicklime
        mg_prop = (vec_loss[
                       5] / bri_evap) * m_saltbri  # Mass of Mg in brine which is required to be removed by adding lime
        lime_low_quality = (mg_prop / Mg * (Ca + O)) * 1.2  # Required mass of low quality quicklime [kg]
        water_lime_low_quality = (lime_low_quality / (Ca + O)) * (
                    H * 2 + O)  # Required mass of water to produce quicklime solution [kg]
        if second_Li_enrichment != 0 :
            brinemass_req2 = second_Li_enrichment/vec_end[0]
            brinemass_proc2 = 1.00
            brinemass_evap2 = brinemass_req2 - brinemass_proc2  # Required mass which needs to be evaporated and precipitated
            m_saltbrine2 = brinemass_evap2 / brinemass_req2 * m_bri_proc
            m_output = m_bri_proc + water_lime_low_quality - m_saltbrine2
        else:
            m_output = m_bri_proc + water_lime_low_quality
            m_saltbrine2 = 0

        return water_lime_low_quality, lime_low_quality, m_output, m_saltbrine2

    def freshwater_usage_proxy(self, proxy_value, m_saltbri, m_saltbrine2):
        m_saltbri = m_saltbri + m_saltbrine2
        water_pipewashing = proxy_value * m_saltbri
        return water_pipewashing

    def diesel_usage_proxy(self, proxy_value, m_saltbri):
        hrs_excav = (proxy_value * m_saltbri)/37  # working hours for excavators TODO check where 37 is coming from
        return hrs_excav

class transport_brine:
    def execute(self, site_parameters, m_in):
        process_name = 'df_transport_brine'
        distance = site_parameters['distance_to_processing'] # distance from evaporation ponds to processing plant
        tkm = (m_in / 1000) * distance # tonne-kilometer of brine transport
        m_output = m_in # no changes in terms of mass

        df_data = {
            'Variables' : [f'm_output_{process_name}', f'm_in_{process_name}', f'transport_{process_name}'],
            'Values' : [m_output, m_in, tkm]
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }

class B_removal_organicsolvent:
    @staticmethod
    def calculate_energy_demand(T_out, T_boron, hCHH_bri, m_bri_proc, heat_loss) :
        return ((T_out - T_boron) * hCHH_bri * m_bri_proc) / 1e6 / heat_loss

    @staticmethod
    def calculate_delta_concentrations(pH_aft, pH_ini, pOH_ini, pOH_aft) :
        delta_H_conc = (10 ** -pH_aft) - (10 ** -pH_ini)
        delta_OH_conc = (10 ** -pOH_ini) - (10 ** -pOH_aft)
        return delta_H_conc, delta_OH_conc

    def calculate_HCl_demand(self, delta_H_conc, delta_OH_conc, m_bri_proc, Dens_end, Dens_ini, vec_end) :
        HCl_pH = (delta_H_conc * m_bri_proc / (1000 * Dens_end) * (H + Cl) +
                  delta_OH_conc * m_bri_proc / (Dens_ini * 1000) * (H + Cl)) / 0.32

        HCl_borate = ((vec_end[7] * 10 * m_bri_proc / B) * 1 * (H * Cl) / 1000) / 0.32
        HCl_sulfate = ((vec_end[6] * 10 * m_bri_proc / (S + O * 4)) * 0.56 * (H * Cl) / 1000) / 0.32
        HCl_mass32 = (HCl_pH + HCl_borate + HCl_sulfate) * 0.32

        return HCl_mass32

    def calculcate_organicsolvent_demand(self, density_enriched_brine, m_in, life) :
        organic = (1 - recycling_rate) * ((m_in / (
                density_enriched_brine * 1000)) * dens_organicsolvent)  # mass of added organic solvent required for concentrated brine [kg/yr]

        organic_invest = (organic / (
                1 - recycling_rate)) / life  # organic solvent which is required at the beginning of the processing activity, divided by the life time of the mine site
        water_SX_strip = ((organic / dens_organicsolvent) / 3) * 1000
        organic_sum = organic + organic_invest
        waste_organic = organic_sum

        return organic_sum, waste_organic, water_SX_strip

    def calculate_NaOH_and_boron_precipitates(self, vec_end, m_in):
        # Boron precipitates estimation
        boron_mass = ((vec_end[7]) / 100 * m_in)  # boron mass in brine [kg]
        nat_boron = boron_mass / B * (1 / 4 * (Na * 2 + B * 4 + O * 7))  # Helene
        sodium_hydroxide = nat_boron / (Na * 2 + B * 4 + O * 7) * 2 * (
                Na + O + H)  # Required mass of sodium hydroxide for the specific production volume [kg] TODO: Efficiency?
        water_sodium_hydroxide = sodium_hydroxide / sodiumhydroxide_solution  # Dissolved sodium hydroxide in aqueous solution [kg]
        return (-nat_boron), sodium_hydroxide, water_sodium_hydroxide, boron_mass


    def execute(self, site_parameters, m_in):
        process_name = 'df_B_removal_orgsolvent'
        T_out = site_parameters['annual_airtemp'] # annual air temperature
        vec_end = site_parameters['vec_end'] # vector of chemical composition of brine in processing facility
        density_initial_brine = site_parameters['density_brine']  # density of initial brine
        density_enriched_brine = site_parameters['density_enriched_brine']  # density of enriched brine
        life = site_parameters['lifetime']  # lifetime of the plant

        # Energy demand for boron removal
        E_boronremoval = self.calculate_energy_demand(T_out, T_boron, hCHH_bri, m_in, heat_loss)  # Energy demand including heat loss [MJ]

        # Organic solvent demand
        # Reduction of pH (pH constants from chemical formulas)

        # Calculate delta concentrations
        delta_H_conc, delta_OH_conc = self.calculate_delta_concentrations(pH_aft, pH_ini, pOH_ini, pOH_aft)

        # Calculate organic solvent demand
        HCl_mass32 = self.calculate_HCl_demand(delta_H_conc, delta_OH_conc, m_in, density_enriched_brine,
                                               density_initial_brine, vec_end)

        # Boron precipitates estimation
        organic, waste_organic, water_SX_strip = self.calculcate_organicsolvent_demand(density_enriched_brine, m_in, life)

        nat_boron, sodium_hydroxide, water_sodium_hydroxide, boron_mass = self.calculate_NaOH_and_boron_precipitates(vec_end, m_in)

        water_sum = water_sodium_hydroxide + water_SX_strip  # Total mass of required deionized water in this process [kg]
        m_output = m_in - boron_mass  # Mass going out of this process [kg]


        df_data = {
            'Variables' : [f'm_output_{process_name}', f'm_in_{process_name}', f'E_{process_name}',
                           f'chemical_HCl_{process_name}', f'chemical_organicsolvent_{process_name}',
                           f'chemical_NaOH_{process_name}', f'water_{process_name}',
                           f'waste_organicsolvent_{process_name}', f'waste_solid_{process_name}'],
            'Values' : [m_output, m_in, E_boronremoval, HCl_mass32, organic, sodium_hydroxide, water_sum,
                        waste_organic, nat_boron]
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }



# Si & Fe removal by precipitation
class SiFe_removal_limestone :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_SiFe_removal_limestone'  # Si and Fe removal by precipitation
        vec_end = site_parameters['vec_end'] # vector of chemical composition of brine
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : Ca_mass_brine,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }

#Mg removal by soda ash
class Mg_removal_sodaash :
    def execute(self, site_parameters, m_in) :
        process_name = "df_Mg_removal_sodaash"
        vec_end = site_parameters['vec_end']  # vector of chemical composition of brine

        motherliq_reported = site_parameters['motherliq_reported'] # if mother liquor is reported, 1 == yes, 0 == no

        sodaash_Mg = (((vec_end[5] / 100) * m_in) / Mg) * (Na * 2 + C + O * 3) * 1.1
        water_soda_Mg = sodaash_Mg / sodaash_solution

        MgCO3_waste = ((vec_end[5] / 100) * m_in / Mg) * (Mg + C + O * 3)
        NaCl_waste = (2 * MgCO3_waste / (Mg + C + O * 3) * (Na + Cl))
        waste_sum = (MgCO3_waste + NaCl_waste)

        if motherliq_reported == 1 :
            motherliq = 5 * m_in
            m_mixbri = m_in + motherliq
            T_mix = (motherliq * T_motherliq + T_Mg_soda * m_in) / m_mixbri


            if T_Mg_soda > T_mix :
                E_Mg = ((T_Mg - T_mix) * hCHH_bri * m_mixbri / 10 ** 6) / heat_loss
            else :
                E_Mg = 0
        else :
            E_Mg = 0
            m_mixbri = m_in


        m_output = m_mixbri + water_soda_Mg + sodaash_Mg

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"E_{process_name}",
                f"chemical_sodaash_{process_name}",
                f"water_sodaash_{process_name}",
                #f"waste_solid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                E_Mg,
                sodaash_Mg,
                water_soda_Mg,
                #waste_sum,
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': waste_sum,
            'waste_centrifuge_quicklime': None
            }

#Mg removal by quicklime
class Mg_removal_quicklime :
    def execute(self, site_parameters, m_in) :
        process_name = "df_Mg_removal_quicklime"
        lime = (((Mg_conc_pulp_quicklime / 100) * m_in) / Mg) * (Ca + O * 2 + H * 2) * quicklime_reaction_factor
        water_lime = (lime / (Ca + O)) * (H * 2 + O)

        waste_Ca = (lime / (Ca + 2 * H + 2 * O)) * (0.66 * (S + Ca + O * 4 + 2 * (H * 2 + O))) #TODO check this factor
        waste_Mg = (lime / (Ca + 2 * H + 2 * O)) * (Mg + H * 2 + O * 2)
        waste_sum = waste_Ca + waste_Mg
        m_output = lime + water_lime + m_in

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"chemical_lime_{process_name}",
                f"water_lime_{process_name}",
                #f"waste_solid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                lime,
                water_lime,
                #waste_sum,
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': waste_sum
            }

class sulfate_removal_calciumchloride :
    def execute(self, site_parameters, m_in):
        process_name = "df_sulfate_removal_calciumchloride"
        vec_end = site_parameters['vec_end']

        waste_sulfate = ((((0.3 * vec_end[6] / 100) * m_in * 1000) / (S + O * 4)) * (
                    Ca + S + O * 4)) / 1000  # Mass of precipitated anhydrite due to calcium chloride [kg]
        calciumchloride = 0.66 * (((((Ca / (Ca + S + O * 4)) * prod_sulfate * 1000) / Ca) * (
                    Ca + Cl * 2)) / 1000)  # 0.3 because Tran and Luong (2015) stated 70 % sulfates already precipitated
        water_calciumchloride = calciumchloride / calciumchloride_solution  # assuming 30 wt. % CaCl2 solution
        m_output = m_in - waste_sulfate + water_CaCl  # Mass going out of this process [kg]

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"chemical_calciumchloride_{process_name}",
                f"water_calciumchloride_{process_name}",
                f"waste_solid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                calciumchloride,
                water_calciumchloride,
                waste_sulfate,
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }

#Ion exchanger - high water demand TODO: repair this function
class ion_exchange_H :
    def execute(self, site_parameters, m_in) :
        process_name = "df_ion_exchange_H"

        elec_IX = 3 * 0.82 * 10 ** (-3) * m_in  # Electricity demand for ion exchanger [kWh]
        water_IX = 3 * 0.5 * (2 * m_in)  # Required mass of deionized water [kg]
        HCl_IX = 3 * 0.24 * 10 ** (-3) * m_in  # HCl demand for ion exchanger [kg]
        NaOH_IX = 3 * 0.12 * 10 ** (-3) * m_in  # NaOH demand for ion exchanger [kg]
        heat_IX = -(3 * 1.62 * 10 ** (-3) * m_in)  # Thermal energy demand for ion exchanger [MJ]
        Cl_IX = -(3 * 0.23 * 10 ** (-3) * m_in)  # Chlorine waste production [kg]
        Na_IX = -(3 * 0.07 * 10 ** (-3) * m_in)  # Sodium waste production [kg]
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }


class triple_evaporator :
    def execute(self, site_parameters, m_in) :
        process_name = 'df_triple_evaporator'

        E_evap = m_in / dens_pulp * 145  # MJ per m3 input
        elec_evap = m_in / dens_pulp * 2  # kWh per m3 input
        steam = (Li_out_RO / Li_out_evaporator * m_in) / evaporator_gor  # taking from geothermal power plant
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
                #f"waste_solid_{process_name}",
                f"water_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                E_Liprec,
                sodaash_Liprec,
                #prod_NaCl2,
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
        waste_heat_sum = -(rel_heat_CO2 + rel_heat_H2O)/ 10 ** 6  # waste heat [MJ]
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }



class CentrifugeBase :
    def __init__(self, process_name, density_key, prod_factor=None, waste_liquid_factor=None, waste_solid_factor=None,
                 recycle_factor=None) :
        self.process_name = process_name
        self.density_key = density_key
        self.prod_factor = prod_factor
        self.waste_liquid_factor = waste_liquid_factor
        self.waste_solid_factor = waste_solid_factor
        self.recycle_factor = recycle_factor

    def execute(self, prod, site_parameters, m_in) :
        # Get the initial density from the site parameters
        density_pulp = site_parameters[self.density_key]

        # Calculate electricity consumption of the centrifuge
        elec_centri = 1.3 * m_in / (density_pulp * 1000)

        if self.prod_factor is None :
            m_output = m_in - waste

        # Calculate the output mass from the centrifuge
        m_output = self.prod_factor * prod

        # Initialize waste and recycled waste
        waste_liquid, waste_solid, recycled_waste = 0, 0, 0

        # Calculate liquid and solid waste if applicable
        if self.waste_liquid_factor is not None :
            waste_liquid = (m_in - m_output) * self.waste_liquid_factor

        if self.waste_solid_factor is not None :
            waste_solid = (m_in - m_output) * self.waste_solid_factor

        # Calculate recycled waste if applicable
        if self.recycle_factor is not None :
            recycled_waste = (m_in - m_output) * self.recycle_factor

        # Compile data for dataframe
        variables = ['m_output', 'm_in', 'elec']
        values = [m_output, m_in, elec_centri]

        if waste_liquid :
            variables.append('waste_liquid')
            values.append(waste_liquid)
        if waste_solid :
            variables.append('waste_solid')
            values.append(waste_solid)
        if recycled_waste :
            variables.append('recycled_waste')
            values.append(recycled_waste)

        df_data = {
            "Variables" : [f"{var}_{self.process_name}" for var in variables],
            "Values" : values
            }

        # Create a dataframe
        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        # Return results in a dictionary
        return {
            'process_name' : self.process_name,
            'm_out' : m_output,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }

class CentrifugeTG(CentrifugeBase) :
    def __init__(self) :
        super().__init__(
            process_name='df_centrifuge_TG',
            density_key='density_brine',
            prod_factor=1.5,
            waste_liquid_factor=-0.8, #/1000
            recycle_factor=0.2 # TODO Adjust recycling flows in the code?
            )


class CentrifugeBG(CentrifugeBase) :
    def __init__(self) :
        super().__init__(
            process_name='df_centrifuge_BG',
            density_key='density_brine',
            prod_factor=1.5,
            waste_liquid_factor=-1  #/1000
            )

class CentrifugeWash(CentrifugeBase) :
    def __init__(self) :
        super().__init__(
            process_name='df_centrifuge_wash',
            density_key='density_brine',
            prod_factor=1.5,
            waste_liquid_factor=-1  #/ 1000
            )


class CentrifugePurification :
    def __init__(self, waste_name) :
        # Ensure the waste_name is valid (non-empty and a string)
        if not isinstance(waste_name, str) or not waste_name.strip() :
            raise ValueError("waste_name must be a non-empty string")
        self.process_name = f'df_centrifuge_purification_{waste_name.strip().lower()}'

    def execute(self, waste, m_in) :
        elec_centri = waste / 100
        m_output = m_in - waste

        # Compile data for dataframe
        variables = ['m_output', 'm_in', 'elec', 'waste_solid']
        values = [m_output, m_in, elec_centri, (- waste)]

        df_data = pd.DataFrame({
            "Variables" : [f"{var}_{self.process_name}" for var in variables],
            "Values" : values
            })
        # Create a dataframe
        df_process = pd.DataFrame(df_data)

        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        # Return results in a dictionary
        return {
            'process_name' : self.process_name,
            'm_out' : m_out,
            'data_frame' : df_process,
            'mass_CO2' : None,
            'prod_libicarb' : None,
            'water_RO' : None,
            'water_evap' : None,
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None
            }

class CentrifugeSoda(CentrifugePurification) :
    def __init__(self) :
        super().__init__(
            waste_name="sodaash"
            )

class CentrifugeQuicklime(CentrifugePurification) :
    def __init__(self) :
        super().__init__(
            waste_name="quicklime"
            )

#Centrifuge with pure information
class Centrifuge_general(CentrifugePurification) :
    def __init__(self) :
        super().__init__(
            waste_name="general"
            )


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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
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
            'Ca_mass_brine' : None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None
            }


# Set up of the site - brine volumes and Li2CO3 production

def setup_site(eff, site_parameters) :
    vec_ini = site_parameters['vec_ini']  # vector of concentrations at the beginning of the process sequence
    Li_conc = vec_ini[0]  # concentration of lithium in the brine

    Dens_ini = site_parameters['density_brine']  # initial density of brine
    v_pumpbrs = site_parameters['brine_vol']  # volume of brine pumped per second
    op_days = site_parameters['operating_days']  # number of operating days per year
    if eff == site_parameters['Li_efficiency'] :
        eff = site_parameters['Li_efficiency']
    else:
        eff = eff # efficiency of lithium extraction
        site_parameters['Li_efficiency'] = eff

    # Mass of brine going into the process sequence
    v_pumpbr = ((v_pumpbrs / 1000) * op_days * 60 * 60 * 24)#/ eff  # volume of brine [m3/yr]
    m_pumpbr = v_pumpbr * Dens_ini * 1000  # mass of pumped brine per year [kg/yr]
    prod_year = (((v_pumpbrs / 1000) * op_days * 24 * 60 * 60 * (1000 * Dens_ini) * (Li_conc / 100)) / (
            (2 * Li) / (2 * Li + C + O * 3)))*eff

    return prod_year, m_pumpbr


def setup_logging(filename) :

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
        setup_logging(filename+".txt")
        self.site_parameters = site_parameters
        self.data_frames = {}
        self.m_in = m_in
        self.prod = prod_initial
        self.dynamic_attributes = {}
        self.process_sequence = process_sequence
        self.process_dependencies = {
            'CaMg_removal_sodiumhydrox': ['MnZn_removal_lime'],
            'Liprec_BG': ['dissolution'],
            'CentrifugeSoda': ['Mg_removal_sodaash'],
            'CentrifugeQuicklime': ['Mg_removal_quicklime']
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
        elif process_type == belt_filter :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == rotary_dryer :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == CentrifugeTG :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == CentrifugeBG :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == CentrifugeWash :
            return (self.prod, self.site_parameters, self.m_in)
        elif process_type == evaporation_ponds :
            return (self.site_parameters, self.m_in)
        elif process_type == B_removal_organicsolvent :
            return (self.site_parameters, self.m_in)
        elif process_type == transport_brine :
            return (self.site_parameters, self.m_in)
        elif process_type == sulfate_removal_calciumchloride :
            return (self.site_parameters, self.m_in)
        elif process_type == Mg_removal_sodaash :
            return (self.site_parameters, self.m_in)
        elif process_type == Mg_removal_quicklime :
            return (self.site_parameters, self.m_in)
        elif process_type == CentrifugeSoda:
            return (self.dynamic_attributes["waste_centrifuge_sodaash"], self.m_in)
        elif process_type == CentrifugeQuicklime:
            return (self.dynamic_attributes["waste_centrifuge_quicklime"], self.m_in)
        elif process_type == Centrifuge_general:
            return(0.05*self.m_in, self.m_in)
        else :
            raise ValueError(f"Unsupported process: {process_type}")


    def run(self, filename):
        setup_logging(filename)

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
                #logging.info(f"Executing {process_name}")
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

    def run_simulation(self, op_location, abbrev_loc, process_sequence, max_eff,
                       min_eff, eff_steps, Li_conc_steps, Li_conc_max, Li_conc_min) :

        eff_range = np.arange(max_eff, min_eff - eff_steps + 0.001, -eff_steps)

        Li_conc_range = [Li_conc_max]
        while Li_conc_range[-1] > Li_conc_min :
            next_value = Li_conc_range[-1] - Li_conc_steps
            if next_value < 0 :
                break
            elif next_value < Li_conc_min :
                next_value = Li_conc_min
            Li_conc_range.append(next_value)

        Li_conc_range = np.array(Li_conc_range)

        results_dict = {}

        for eff in eff_range :
            results_dict[eff] = {}
            for Li in Li_conc_range :
                filename = f"{abbrev_loc}_eff{eff}_Li{Li}.txt"

                initial_data = extract_data(op_location, abbrev_loc, Li)

                prod, m_pumpbr = setup_site(eff, site_parameters=initial_data[abbrev_loc])
                print(f"Efficiency: {eff}")
                print(f"Production: {prod}")
                print(f"Mass of brine: {m_pumpbr}")

                manager = ProcessManager(initial_data[abbrev_loc], m_pumpbr, prod, process_sequence, filename)

                result_df = manager.run(filename)

                energy_per_prod_mass, elec_per_prod_mass, water_per_prod_mass = manager.calculate_resource_per_prod_mass(
                    result_df, prod)

                results_dict[eff][Li] = {
                    'data_frames' : result_df,
                    'resources_per_kg' : (energy_per_prod_mass, elec_per_prod_mass, water_per_prod_mass)
                    }

        with open(f"results_dict_{abbrev_loc}_{Li}_{eff}.pkl", "wb") as f :
            pickle.dump(results_dict, f)

        print("Simulation completed and results stored in the dictionary.")

        viz = Visualization()
        viz.plot_resources_per_kg(results_dict, abbrev_loc)

        return results_dict, eff_range, Li_conc_range




