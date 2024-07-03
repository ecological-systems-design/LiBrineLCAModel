from src.LifeCycleInventoryModel_Li.operational_and_environmental_constants import *

from src.LifeCycleInventoryModel_Li.import_site_parameters import *

from src.Postprocessing_results.visualization_functions import Visualization



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
    def execute(self,site_parameters,m_in,prod,constants,params) :
        process_name = 'df_evaporation_ponds'

        # Retrieve parameters
        op_days = params.get('op_days',site_parameters['operating_days'])  # Operational days per year
        vec_ini = site_parameters['vec_ini']  # vector of chemical composition of initial brine
        vec_end = site_parameters[
            'vec_end']  # vector of chemical composition of enriched brine sent to processing plant
        density_initial_brine = site_parameters['density_brine']  # density of initial brine
        density_enriched_brine = site_parameters['density_enriched_brine']  # density of enriched brine
        evaporation_rate = params.get('evaporation_rate',site_parameters[
            'evaporation_rate'])  # evaporation rate of brine in evaporation ponds
        quicklime_reported = site_parameters[
            'quicklime_reported']  # question if quicklime is used or not in the evaporation ponds
        freshwater_reported = site_parameters[
            'freshwater_reported']  # question if freshwater is reported or not in the evaporation ponds
        freshwater_vol = site_parameters[
            'freshwater_vol']  # volume of freshwater pumped to the surface at evaporation ponds [L/s]
        brine_vol = site_parameters['brine_vol']  # volume of brine pumped to the surface at evaporation ponds [L/s]
        overall_efficiency = site_parameters['Li_efficiency']  # overall efficiency
        second_Li_enrichment_reported = site_parameters[
            'second_Li_enrichment_reported']  # question if second Li enrichment is reported or not in the evaporation ponds
        second_Li_enrichment = site_parameters[
            'second_Li_enrichment']  # second Li enrichment, either 0 or reported value
        diesel_reported = site_parameters[
            'diesel_reported']  # question if diesel is reported or not in the evaporation ponds
        depth_well_brine = site_parameters['well_depth_brine']  # depth of the well for brines
        depth_well_freshwater = site_parameters['well_depth_freshwater']  # depth of the well for freshwater
        life = params.get('lifetime',site_parameters['lifetime'])

        # Retrieve constants
        gravity_constant = constants['gravity_constant']
        eff_pw = params.get('eff_pw', constants['eff_pw'])
        proxy_saltremoval = params.get('proxy_saltremoval', constants['proxy_saltremoval'])
        proxy_salt_ATACAMA = params.get('proxy_salt_ATACAMA', constants['proxy_salt_ATACAMA'])
        proxy_quicklime_OLAROZ = params.get('proxy_quicklime_OLAROZ', constants['proxy_quicklime_OLAROZ'])
        dens_frw = constants['dens_frw']
        sulfuricacid_solution = params.get('sulfuricacid_solution', constants['sulfuricacid_solution'])
        hCHH_bri = constants['hCHH_bri']
        heat_loss = params.get('heat_loss', constants['heat_loss'])
        Ca = constants['Ca']
        O = constants['O']
        H = constants['H']
        Mg = constants['Mg']
        working_hours_excavator = params.get('working_hours_excavator', constants['working_hours_excavator'])

        proxy_harvest = params.get('proxy_harvest', constants['proxy_harvest'])
        proxy_freshwater_EP = params.get('proxy_freshwater_EP', constants['proxy_freshwater_EP'])


        operating_time = op_days * 24 * 60 * 60  # Operating time in seconds
        m_in_initial = m_in

        # Volume and mass changes during evaporation
        if round(vec_end[0],4) != round(vec_ini[0],4) :
            brinemass_req = vec_end[0] / (
                        vec_ini[0] * overall_efficiency)  # Required mass of brine to gain 1 kg concentrated brine
        else :
            brinemass_req = round(vec_end[0],4) / round(vec_ini[0],4)
            m_in = m_in / overall_efficiency
        brinemass_proc = 1.00
        brinemass_evap = brinemass_req - brinemass_proc  # Required mass which needs to be evaporated and precipitated

        # Elemental losses during evaporation based on chemical composition
        vec_loss = [
            (brinemass_req * (vec_ini[i] / 100) - (vec_end[i] / 100) * brinemass_proc)
            if not math.isnan(vec_ini[i]) and not math.isnan(vec_end[i])
            else float('nan')
            for i in range(len(vec_end))
            ]

        epsilon = 1e-20  # Tolerance level for the elemental losses

        if any((loss < -epsilon or loss > epsilon) and not np.isnan(loss) for loss in vec_loss) :
            # Calculation of precipitated salts and brine sent to the processing plant
            m_saltbrine_removed = brinemass_evap / brinemass_req * m_in
            # Sum only non-nan values in vec_loss
            total_loss = np.nansum(vec_loss)

            # Exclude the last element if it is nan in the total_loss calculation
            if np.isnan(vec_loss[15]) :
                m_salt = ((vec_end[0] / vec_ini[0]) / proxy_saltremoval) * proxy_salt_ATACAMA
            else :
                total_loss_excluding_last = total_loss - vec_loss[15]
                m_salt = (total_loss_excluding_last / total_loss) * m_saltbrine_removed

            m_in = m_in - m_saltbrine_removed

            # Quicklime demand if reported
            if quicklime_reported == 1 :
                water_quicklime,chemical_quicklime,m_saltbrine2 = self.quicklime_usage(vec_loss,vec_ini,vec_end,
                                                                                       m_saltbrine_removed,m_in,
                                                                                       brinemass_evap,
                                                                                       second_Li_enrichment,prod,
                                                                                       m_in_initial,constants,params)
            else :
                water_quicklime = 0
                chemical_quicklime = 0
                m_saltbrine2 = 0

            # Freshwater demand if reported
            if freshwater_reported == 1 :
                water_pipewashing = (
                                                freshwater_vol / 1000) * dens_frw * operating_time  # mass of fresh water pumped per year [kg/year], in evaporation ponds
                sulfuric_acid = sulfuricacid_solution * water_pipewashing * 0.01
            else :
                water_pipewashing = self.freshwater_usage_proxy(proxy_freshwater_EP,m_saltbrine_removed,m_saltbrine2,constants,params)
                sulfuric_acid = sulfuricacid_solution * water_pipewashing * 0.01
                depth_well_freshwater = 0.1 * depth_well_brine  # depth of the well for freshwater, assuming 10 % of the depth of the brine well
                freshwater_vol = (water_pipewashing / (dens_frw * 1000)) / operating_time

            # Overall water demand in evaporation ponds
            water_evaporationponds = water_pipewashing + water_quicklime

            # Land use to produce 1 kg concentrated brine
            area_occup = brinemass_evap / 1000 / evaporation_rate
            transf = area_occup / life
        else :
            area_occup = 0
            transf = 0
            m_saltbrine_removed = 0
            m_saltbrine2 = 0
            water_evaporationponds = 0.05 * m_in  # 5 % of m_in is required to wash the pumps and pipes, rough assumption
            chemical_quicklime = 0
            sulfuric_acid = sulfuricacid_solution * water_evaporationponds * 0.01
            water_pipewashing = water_evaporationponds
            water_quicklime = 0
            m_salt = 0
            freshwater_vol = water_evaporationponds / (dens_frw * 1000) / operating_time

        m_Li = (m_in_initial * vec_ini[0]) / 100  # mass of lithium in the annual pumped brine [kg]

        # Well field system
        power_well = gravity_constant * (
                density_initial_brine * brine_vol * depth_well_brine + freshwater_vol * depth_well_freshwater) / eff_pw  # Electricity for pumping activity of wells required for brine and fresh water [kWh]
        electric_well = power_well * 1.1 * (1 / (3600 * 1000)) * operating_time

        # Salt harvesting until processing plant
        if diesel_reported == 1 :
            hrs_excav = site_parameters['diesel_consumption'] / working_hours_excavator  # working hours for excavators
        else :
            hrs_excav = self.diesel_usage_proxy(proxy_harvest,m_saltbrine_removed,constants,params)

        waste_water = water_pipewashing

        m_output = m_in - m_saltbrine2 + water_quicklime

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
                        chemical_quicklime, sulfuric_acid, (-m_salt), waste_water]
            }

        df_process = pd.DataFrame(df_data)
        df_process['per kg'] = df_process['Values'] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]['Values']
        #print(df_process)

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
            'waste_centrifuge_quicklime': None,
            'motherliq' : None,
            'water_NF': None
            }

    def quicklime_usage(self,vec_loss,vec_ini,vec_end,m_saltbri,m_bri_proc,bri_evap,second_Li_enrichment,prod,
                        m_in_initial,constants,params) :
        """
        Calculate quicklime usage and related parameters.

        :param vec_loss: List of elemental losses during evaporation.
        :param vec_ini: Vector of chemical composition of initial brine.
        :param vec_end: Vector of chemical composition of enriched brine.
        :param m_saltbri: Mass of salt in brine.
        :param m_bri_proc: Mass of concentrated brine sent to processing plant.
        :param bri_evap: Required mass which needs to be evaporated and precipitated.
        :param second_Li_enrichment: Second Li enrichment value.
        :param prod: Production value.
        :param m_in_initial: Initial mass input.
        :param constants: Dictionary of constants.
        :param params: Dictionary of parameters.
        :return: Tuple of water lime low quality, lime low quality, output mass, and salt brine mass for second enrichment.
        """
        # Retrieve constants
        Ca = constants['Ca']
        O = constants['O']
        H = constants['H']
        Mg = constants['Mg']
        proxy_quicklime_OLAROZ = params.get('proxy_quicklime_OLAROZ', constants['proxy_quicklime_OLAROZ'])

        # Check if each element in vec_loss is NaN
        is_nan_vec_loss_except_first = [math.isnan(loss) for loss in vec_loss[1 :]]

        # Now, if you want to perform an action based on this
        if all(is_nan_vec_loss_except_first) :
            # Missing information on chemistry of brine when sent to processing plant
            lime_low_quality = proxy_quicklime_OLAROZ * m_in_initial * vec_ini[5]
            water_lime_low_quality = (lime_low_quality / (Ca + O)) * (H * 2 + O)

            if not np.isnan(second_Li_enrichment) :
                brinemass_req2 = second_Li_enrichment / vec_end[0]
                brinemass_proc2 = 1.00
                brinemass_evap2 = brinemass_req2 - brinemass_proc2
                m_saltbrine2 = brinemass_evap2 / brinemass_req2 * m_bri_proc
            else :
                m_saltbrine2 = 0

        else :
            # First magnesium and calcium removal by adding low quality quicklime
            mg_prop = (vec_loss[
                           5] / bri_evap) * m_saltbri  # Mass of Mg in brine which is required to be removed by adding lime
            lime_low_quality = (mg_prop / Mg * (Ca + O)) * 1.2  # Required mass of low quality quicklime [kg]
            water_lime_low_quality = (lime_low_quality / (Ca + O)) * (
                        H * 2 + O)  # Required mass of water to produce quicklime solution [kg]
            if not np.isnan(second_Li_enrichment) :
                brinemass_req2 = second_Li_enrichment / vec_end[0]
                brinemass_proc2 = 1.00
                brinemass_evap2 = brinemass_req2 - brinemass_proc2  # Required mass which needs to be evaporated and precipitated
                m_saltbrine2 = brinemass_evap2 / brinemass_req2 * m_bri_proc
            else :
                m_saltbrine2 = 0

        return water_lime_low_quality,lime_low_quality,m_saltbrine2

    def freshwater_usage_proxy(self,proxy_value,m_saltbri,m_saltbrine2,constants,params) :
        """
        Calculate freshwater usage based on proxy value and salt brine mass.

        :param proxy_value: Proxy value for freshwater usage.
        :param m_saltbri: Mass of salt brine.
        :param m_saltbrine2: Mass of salt brine for second enrichment.
        :param constants: Dictionary of constants.
        :param params: Dictionary of parameters.
        :return: Water usage for pipe washing.
        """
        m_saltbri = m_saltbri + m_saltbrine2
        water_pipewashing = proxy_value * m_saltbri
        return water_pipewashing

    def diesel_usage_proxy(self,proxy_value,m_saltbri,constants,params) :
        """
        Calculate diesel usage based on proxy value and salt brine mass.

        :param proxy_value: Proxy value for diesel usage.
        :param m_saltbri: Mass of salt brine.
        :param constants: Dictionary of constants.
        :param params: Dictionary of parameters.
        :return: Working hours for excavators.
        """
        # Retrieve constants
        working_hours_excavator = params.get('working_hours_excavator', constants['working_hours_excavator'])

        hrs_excav = (proxy_value * m_saltbri) / working_hours_excavator  # working hours for excavators
        return hrs_excav


class DLE_evaporation_ponds :
    def execute(self,site_parameters,m_in,constants,params) :
        process_name = 'df_DLE_evaporation_ponds'

        # Use params if provided, otherwise fallback to site_parameters or constants
        life = params.get('lifetime',site_parameters['lifetime'])
        Li_out_EP_DLE = params.get('Li_out_EP_DLE',constants['Li_out_EP_DLE'])

        Li_in_EP_DLE = 0.9 * Li_out_EP_DLE
        m_output = Li_in_EP_DLE / Li_out_EP_DLE * m_in

        water_evaporationponds = 0.1 * m_in  # 10% of m_in is required to wash the pumps and pipes, rough assumption
        waste_water = water_evaporationponds

        area_occup = 0
        transf = 0  # Set to 0; how to calculate can be done at a later point; land use not a major focus of this project

        df_data = {
            'Variables' : [
                f'm_output_{process_name}',
                f'm_in_{process_name}',
                f'water_{process_name}',
                f'land_occupation_{process_name}',
                f'land_transform_unknown_{process_name}',
                f'land_transform_minesite_{process_name}',
                f'waste_liquid_{process_name}'
                ],
            'Values' : [
                m_output,
                m_in,
                water_evaporationponds,
                area_occup,
                transf,
                transf,
                waste_water
                ]
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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }


class transport_brine :
    def execute(self,site_parameters,m_in,constants,params) :
        process_name = 'df_transport_brine'

        # Use params if provided, otherwise fallback to site_parameters
        distance = params.get('distance_to_processing',site_parameters[
            'distance_to_processing'])  # distance from evaporation ponds to processing plant

        tkm = (m_in / 1000) * distance  # tonne-kilometer of brine transport
        m_output = m_in  # no changes in terms of mass

        df_data = {
            'Variables' : [f'm_output_{process_name}',f'm_in_{process_name}',f'transport_{process_name}'],
            'Values' : [m_output,m_in,tkm]
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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }

class B_removal_organicsolvent:
    @staticmethod
    def calculate_energy_demand(T_out, T_boron, hCHH_bri, m_bri_proc, heat_loss):
        if T_out > T_boron:
            E_boron = ((T_out - T_boron) * hCHH_bri * m_bri_proc) / 1e6 / heat_loss
        else:
            E_boron = ((T_out - T_boron) * hCHH_bri * m_bri_proc) / 1e6  # Waste heat from boron removal [MJ]
        return E_boron

    @staticmethod
    def calculate_delta_concentrations(pH_aft, pH_ini, pOH_ini, pOH_aft):
        delta_H_conc = (10 ** -pH_aft) - (10 ** -pH_ini)
        delta_OH_conc = (10 ** -pOH_ini) - (10 ** -pOH_aft)
        return delta_H_conc, delta_OH_conc

    def calculate_HCl_demand(self, delta_H_conc, delta_OH_conc, m_bri_proc, Dens_end, Dens_ini, vec_end, constants):
        HCl_pH = (delta_H_conc * m_bri_proc / (1000 * Dens_end) * (constants['H'] + constants['Cl']) +
                  delta_OH_conc * m_bri_proc / (Dens_ini * 1000) * (constants['H'] + constants['Cl'])) / 0.32

        HCl_borate = ((vec_end[7] * 10 * m_bri_proc / constants['B']) * 1 * (constants['H'] * constants['Cl']) / 1000) / 0.32
        HCl_sulfate = ((vec_end[6] * 10 * m_bri_proc / (constants['S'] + constants['O'] * 4)) * 0.56 * (constants['H'] * constants['Cl']) / 1000) / 0.32
        HCl_mass32 = (HCl_pH + HCl_borate + HCl_sulfate) * 0.32

        return HCl_mass32

    def calculcate_organicsolvent_demand(self, density_enriched_brine, m_in, life, recycling_rate, constants):

        organic = (1 - recycling_rate) * ((m_in / (density_enriched_brine * 1000)) * constants['dens_organicsolvent'])

        organic_invest = (organic / (1 - recycling_rate)) / life
        water_SX_strip = ((organic / constants['dens_organicsolvent']) / 3) * 1000
        organic_sum = organic + organic_invest
        waste_organic = (1 - recycling_rate) * organic_sum

        return organic_sum, waste_organic, water_SX_strip

    def calculate_NaOH_and_boron_precipitates(self, vec_end, m_in, sodiumhydroxide_solution, constants):

        boron_mass = ((vec_end[7]) / 100 * m_in)
        nat_boron = -(boron_mass / constants['B'] * (1 / 4 * (constants['Na'] * 2 + constants['B'] * 4 + constants['O'] * 7)))
        sodium_hydroxide = nat_boron / (constants['Na'] * 2 + constants['B'] * 4 + constants['O'] * 7) * 2 * (constants['Na'] + constants['O'] + constants['H'])
        water_sodium_hydroxide = sodium_hydroxide / sodiumhydroxide_solution
        return nat_boron, -sodium_hydroxide, water_sodium_hydroxide, boron_mass

    def execute(self, site_parameters, m_in, constants, params):
        process_name = 'df_B_removal_orgsolvent'

        # Use params if provided, otherwise fallback to site_parameters or constants
        T_out = params.get('annual_airtemp', site_parameters['annual_airtemp'])
        T_boron = params.get('T_boron', constants['T_boron'])
        hCHH_bri = params.get('hCHH_bri', constants['hCHH_bri'])
        heat_loss = params.get('heat_loss', constants['heat_loss'])
        pH_aft = params.get('pH_aft', constants['pH_aft'])
        pH_ini = params.get('pH_ini', constants['pH_ini'])
        pOH_ini = params.get('pOH_ini', constants['pOH_ini'])
        pOH_aft = params.get('pOH_aft', constants['pOH_aft'])
        recycling_rate = params.get('recycling_rate', constants['recycling_rate'])
        dens_organicsolvent = params.get('dens_organicsolvent', constants['dens_organicsolvent'])
        sodiumhydroxide_solution = params.get('sodiumhydroxide_solution', constants['sodiumhydroxide_solution'])

        vec_end = site_parameters['vec_end']
        density_initial_brine = site_parameters['density_brine']
        density_enriched_brine = site_parameters['density_enriched_brine']
        life = site_parameters['lifetime']

        E_boronremoval = self.calculate_energy_demand(T_out, T_boron, hCHH_bri, m_in, heat_loss)

        if E_boronremoval < 0:
            energy_variable_name = f'waste_heat_{process_name}'
        else:
            energy_variable_name = f'E_{process_name}'

        delta_H_conc, delta_OH_conc = self.calculate_delta_concentrations(pH_aft, pH_ini, pOH_ini, pOH_aft)
        HCl_mass32 = self.calculate_HCl_demand(delta_H_conc, delta_OH_conc, m_in, density_enriched_brine, density_initial_brine, vec_end, constants)

        organic, waste_organic, water_SX_strip = self.calculcate_organicsolvent_demand(density_enriched_brine, m_in, life, recycling_rate, constants)
        nat_boron, sodium_hydroxide, water_sodium_hydroxide, boron_mass = self.calculate_NaOH_and_boron_precipitates(vec_end, m_in, sodiumhydroxide_solution, constants)

        water_sum = water_sodium_hydroxide + water_SX_strip
        m_output = m_in - boron_mass

        df_data = {
            'Variables': [f'm_output_{process_name}', f'm_in_{process_name}', energy_variable_name,
                          f'chemical_HCl_{process_name}', f'chemical_organicsolvent_{process_name}',
                          f'chemical_NaOH_{process_name}', f'water_{process_name}',
                          f'waste_organicsolvent_{process_name}', f'waste_solid_{process_name}'],
            'Values': [m_output, m_in, E_boronremoval, HCl_mass32, organic, sodium_hydroxide, water_sum,
                       waste_organic, nat_boron]
        }

        df_process = pd.DataFrame(df_data)
        df_process['per kg'] = df_process['Values'] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]['Values']

        return {
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }




# Si & Fe removal by precipitation
class SiFeRemovalLimestone:
    def __init__(self):
        self.process_name = 'df_SiFe_removal_limestone'

    def calculate_masses(self, vec_end, m_in):
        fe_mass = (vec_end[-5] / 100) * m_in
        si_mass = (vec_end[-8] / 100) * m_in
        return fe_mass, si_mass

    def calculate_limestone_and_waste(self, fe_mass, si_mass, constants):
        limestone_fe = (fe_mass / constants['Fe']) * (constants['Ca'] + constants['C'] + 3 * constants['O']) * 1.1
        limestone_si = (si_mass / constants['Si']) * (constants['Ca'] + constants['C'] + 3 * constants['O']) * 1.1
        waste_fe_si = -(fe_mass / constants['Fe']) * (3 * constants['Ca'] + 2 * constants['Fe'] + 3 * constants['Si'] + 12 * constants['O'])
        return limestone_fe + limestone_si, waste_fe_si

    def create_dataframe(self, m_output, m_in, vec_end, limestone, waste):
        df_data = {
            'Variables': [f'm_output_{self.process_name}', f'm_Li_{self.process_name}', f'E_{self.process_name}',
                          f'chemical_limestone_{self.process_name}', f'waste_solid_{self.process_name}'],
            'Values': [m_output, m_in * vec_end[0] / 100, 0, limestone, waste]
        }
        df_process = pd.DataFrame(df_data)
        df_process['per kg'] = df_process['Values'] / df_process.iloc[0][1]
        return df_process

    def execute(self, site_parameters: dict, m_in: float, constants: dict, params: dict) -> dict:
        vec_end = site_parameters['vec_end']
        fe_mass, si_mass = self.calculate_masses(vec_end, m_in)
        limestone, waste = self.calculate_limestone_and_waste(fe_mass, si_mass, constants)
        m_output = m_in + waste + limestone
        df_process = self.create_dataframe(m_output, m_in, vec_end, limestone, waste)

        return {
            'process_name': self.process_name,
            'm_out': df_process.iloc[0]['Values'],
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }



# Mn and Zn removal by precipitation
class MnZn_removal_lime :
    def execute(self,site_parameters,m_in,constants,params) :
        process_name = 'df_MnZn_removal_lime'

        # Use params if provided, otherwise fallback to site_parameters or constants
        vec_end = site_parameters['vec_end']

        # Use constant values
        Mn = constants['Mn']
        Zn = constants['Zn']
        Ca = constants['Ca']
        H = constants['H']
        O = constants['O']

        quicklime_reaction_factor = params.get('quicklime_reaction_factor',constants['quicklime_reaction_factor'])

        E_MnZn = 0  # Heating necessary?

        Mn_mass = vec_end[-6] / 100 * m_in
        Zn_mass = vec_end[-4] / 100 * m_in

        lime_MnZn = (Mn_mass / Mn + Zn_mass / Zn) * (Ca + 2 * (O + H)) * quicklime_reaction_factor
        water_lime = (lime_MnZn / (Ca + O)) * (H * 2 + O)

        waste_Mn = -(Mn_mass / Mn * (Mn + 2 * (O + H)))
        waste_Zn = -(Zn_mass / Zn * (Zn + 2 * (O + H)))
        waste_sum = waste_Mn + waste_Zn

        Ca_mass_brine = Ca / (Ca + constants['C'] + 3 * O) * lime_MnZn
        m_output = m_in + waste_Mn + waste_Zn + Ca_mass_brine + lime_MnZn + water_lime

        df_data = {
            'Variables' : [f'm_output_{process_name}',f'm_in_{process_name}',f'E_{process_name}',
                           f'chemical_lime_{process_name}',f'water_{process_name}',f'waste_solid_{process_name}',
                           f'Ca_mass_{process_name}'],
            'Values' : [m_output,m_in,E_MnZn,lime_MnZn,water_lime,waste_sum,Ca_mass_brine]
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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }


# acidification & ion exchanger, T = 30 - 100 °C, pH adaption
class acidification :
    def execute(self,site_parameters,m_in,constants,params) :
        process_name = 'df_acidification'

        # Use params if provided, otherwise fallback to site_parameters or constants
        Dens_ini = site_parameters['density_brine']
        vec_end = site_parameters['vec_end']

        # Use constant values or parameters
        H = constants['H']
        Cl = constants['Cl']
        B = constants['B']
        S = constants['S']
        O = constants['O']

        pH_ini = params.get('pH_ini',constants['pH_ini'])
        pOH_ini = params.get('pOH_ini',constants['pOH_ini'])
        pH_aft = params.get('pH_aft',constants['pH_aft'])
        pOH_aft = params.get('pOH_aft',constants['pOH_aft'])

        delta_H_conc = (10 ** -pH_aft) - (10 ** -pH_ini)
        delta_OH_conc = (10 ** -pOH_ini) - (10 ** -pOH_aft)

        HCl_pH = (((delta_H_conc * (m_in / (1000 * Dens_ini)) * (H + Cl) + delta_OH_conc * (
                    m_in / (Dens_ini * 1000)) * (H + Cl))) / 0.32)
        HCl_borate = ((vec_end[7] * 10 * m_in / B) * 1 * (H * Cl) / 1000) / 0.32
        HCl_sulfate = ((vec_end[6] * 10 * m_in / (S + O * 4)) * 0.56 * (H * Cl) / 1000) / 0.32

        HCl_mass32 = (HCl_pH + HCl_borate + HCl_sulfate) * 0.32
        m_output = m_in + HCl_mass32

        df_data = {
            'Variables' : [f'm_output_{process_name}',f'm_in_{process_name}',f'chemical_HCl_{process_name}'],
            'Values' : [m_output,m_in,HCl_mass32]
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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }

# Li-ion selective adsorption
class Li_adsorption:
    def execute(self, prod, site_parameters, m_in, constants, params):
        process_name = 'df_Li_adsorption'
        life = site_parameters['lifetime']
        T_out = site_parameters['annual_airtemp']
        deposit_type = site_parameters['deposit_type']
        process_sequence = site_parameters['process_sequence']
        print(f'Running function with: {params}')

        Li = constants['Li']
        C = constants['C']
        O = constants['O']
        dens_H2O = constants['dens_H2O']
        T_desorp = params.get('T_desorp', constants['T_desorp'])
        T_adsorp = params.get('T_adsorp', constants['T_adsorp'])
        T_Mg_soda = params.get('T_Mg_soda', constants['T_Mg_soda'])
        hCHH = params.get('hCHH', constants['hCHH'])
        hCHH_bri = params.get('hCHH_bri', constants['hCHH_bri'])
        heat_loss = params.get('heat_loss', constants['heat_loss'])

        adsorb_capacity_salar = params.get('adsorb_capacity_salar', constants['adsorb_capacity_salar'])

        adsorp_capacity = params.get('adsorp_capacity', constants['adsorp_capacity'])
        Li_out_adsorb = params.get('Li_out_adsorb', constants['Li_out_adsorb'])
        water_adsorbent_factor = params.get('water_adsorption_factor', constants['water_adsorption_factor'])
        electricity_adsorption = params.get('electricity_adsorption', constants['electricity_adsorption'])

        adsorbent_loss = prod * ((2 * Li) / (2 * Li + C + 3 * O)) * 1.25
        waste_adsorbent = -adsorbent_loss

        if deposit_type == 'salar':
            adsorbent_invest = prod * ((2 * Li) / (2 * Li + C + 3 * O)) / adsorb_capacity_salar
        else:
            adsorbent_invest = prod * ((2 * Li) / (2 * Li + C + 3 * O)) / adsorp_capacity
        adsorbent = (adsorbent_invest / life) + adsorbent_loss

        if deposit_type == 'salar':
            water_adsorbent = water_adsorbent_factor * adsorbent_invest
            mg_index = process_sequence.index('Mg_removal_sodaash') if 'Mg_removal_sodaash' in process_sequence else -1
            li_index = process_sequence.index('Li_adsorption') if 'Li_adsorption' in process_sequence else -1

            if mg_index != -1 and li_index != -1 and mg_index < li_index:
                E_adsorp = (((T_desorp - T_out) * hCHH * water_adsorbent) + ((T_adsorp - T_Mg_soda) * hCHH_bri * m_in) / 10 ** 6) / heat_loss
            else:
                E_adsorp = (((T_desorp - T_out) * hCHH * water_adsorbent) + ((T_adsorp - T_out) * hCHH_bri * m_in) / 10 ** 6) / heat_loss
        else:
            water_adsorbent = water_adsorbent_factor * adsorbent_invest
            E_adsorp = (((T_desorp - T_out) * hCHH * water_adsorbent) / 10 ** 6) / heat_loss

        elec_adsorp = electricity_adsorption * (m_in + water_adsorbent)
        m_output = water_adsorbent

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"chemical_adsorbent_{process_name}",
                f"water_adsorbent_{process_name}",
                f"elec_adsorp_{process_name}",
                f"E_adsorp_{process_name}",
                f'waste_solid_{process_name}'
            ],
            "Values": [
                m_output,
                m_in,
                adsorbent,
                water_adsorbent,
                elec_adsorp,
                E_adsorp,
                waste_adsorbent
            ],
        }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }

    def update_adsorption_RO_evaporator(df_adsorption,water_RO,water_evap,df_reverse_osmosis,df_triple_evaporator,
                                        constants,params,site_parameters) :
        T_out = site_parameters['annual_airtemp']
        T_desorp = params.get('T_desorp',constants['T_desorp'])
        hCHH = params.get('hCHH',constants['hCHH'])
        heat_loss = params.get('heat_loss',constants['heat_loss'])

        new_value = df_adsorption.iloc[3,1] - water_RO - water_evap
        df_adsorption.loc[3,'Values'] = new_value

        new_value_kg = df_adsorption.iloc[3,2] - (water_RO / df_adsorption.iloc[0,1]) - (
                    water_evap / df_adsorption.iloc[0,1])
        df_adsorption.loc[3,'per kg'] = new_value_kg

        backflow_ro = df_reverse_osmosis.iloc[1,1] - df_reverse_osmosis.iloc[0,1]
        df_reverse_osmosis.loc[len(df_reverse_osmosis.index)] = ['backflow_ro',backflow_ro,0]

        backflow_evap = df_triple_evaporator.iloc[1,1] - df_triple_evaporator.iloc[0,1]
        df_triple_evaporator.loc[len(df_triple_evaporator.index)] = ['backflow_evap',backflow_evap,0]

        E_adsorp_adapted = (((T_desorp - T_out) * hCHH * df_adsorption.iloc[3,1]) / 10 ** 6) / heat_loss
        df_adsorption.loc[5,'Values'] = E_adsorp_adapted
        df_adsorption.loc[5,'per kg'] = E_adsorp_adapted / df_adsorption.iloc[0,1]

        return df_adsorption,df_reverse_osmosis,df_triple_evaporator

    def update_adsorption_nanofiltration_RO(df_adsorption,water_NF,water_RO,df_nanofiltration,df_reverse_osmosis,
                                            constants,params,site_parameters) :
        new_value = df_adsorption.iloc[3,1] - water_NF - water_RO
        print(f'Saving of water due to re-circulation: {(water_NF + water_RO) / df_adsorption.iloc[3,1] * 100} %')
        df_adsorption.loc[3,'Values'] = new_value
        T_out = site_parameters['annual_airtemp']

        new_value_kg = df_adsorption.iloc[3,2] - (water_NF / df_adsorption.iloc[0,1]) - (
                    water_RO / df_adsorption.iloc[0,1])
        df_adsorption.loc[3,'per kg'] = new_value_kg

        if new_value < 0 :
            new_value = 0
            new_value_kg = 0

        df_adsorption.loc[3,'Values'] = new_value
        df_adsorption.loc[3,'per kg'] = new_value_kg

        T_nano = params.get('T_nano',constants['T_nano'])
        T_desorp = params.get('T_desorp',constants['T_desorp'])
        T_adsorp = params.get('T_adsorp',constants['T_adsorp'])
        hCHH = params.get('hCHH',constants['hCHH'])
        hCHH_bri = params.get('hCHH_bri',constants['hCHH_bri'])
        heat_loss = params.get('heat_loss',constants['heat_loss'])

        if T_nano > T_desorp :
            E_water_nano = (((T_nano - T_desorp) * hCHH * (water_NF + water_RO)) / 10 ** 6) * heat_loss
            E_adsorp_without_nano_water = (((T_adsorp - T_out) * hCHH_bri * df_adsorption.iloc[
                1,1]) / 10 ** 6) / heat_loss
            E_adsorp_adapted = E_adsorp_without_nano_water - E_water_nano
            if E_adsorp_adapted < 0 :
                E_adsorp_adapted = 0
        else :
            E_adsorp_adapted = ((((T_desorp - T_out) * hCHH * df_adsorption.iloc[3,1]) + (
                        (T_adsorp - T_out) * hCHH_bri * df_adsorption.iloc[1,1])) / 10 ** 6) / heat_loss

        df_adsorption.loc[5,'Values'] = E_adsorp_adapted
        df_adsorption.loc[5,'per kg'] = E_adsorp_adapted / df_adsorption.iloc[0,1]

        return df_adsorption,df_nanofiltration,df_reverse_osmosis

    def update_adsorption_evaporator(df_adsorption,water_evap,df_triple_evaporator,constants,params,site_parameters) :
        water_evap_in = water_evap
        process_sequence = site_parameters['process_sequence']
        T_out = site_parameters['annual_airtemp']
        deposit_type = site_parameters['deposit_type']
        T_evap = params.get('T_evap',constants['T_evap'])
        T_desorp = params.get('T_desorp',constants['T_desorp'])
        T_adsorp = params.get('T_adsorp',constants['T_adsorp'])
        T_Mg_soda = params.get('T_Mg_soda',constants['T_Mg_soda'])
        hCHH = params.get('hCHH',constants['hCHH'])
        hCHH_bri = params.get('hCHH_bri',constants['hCHH_bri'])
        heat_loss = params.get('heat_loss',constants['heat_loss'])

        new_value = df_adsorption.iloc[3,1] - water_evap
        new_value_kg = df_adsorption.iloc[3,2] - (water_evap / df_adsorption.iloc[0,1])

        if new_value < 0 :
            new_value = 0
            new_value_kg = 0
            water_evap = water_evap - df_adsorption.iloc[3,1]

        df_adsorption.loc[3,'Values'] = new_value
        df_adsorption.loc[3,'per kg'] = new_value_kg

        backflow_evap = df_triple_evaporator.iloc[1,1] - df_triple_evaporator.iloc[0,1]
        df_triple_evaporator.loc[len(df_triple_evaporator.index)] = ['backflow_evap',water_evap,0]

        if deposit_type == "salar" :
            mg_index = process_sequence.index('Mg_removal_sodaash') if 'Mg_removal_sodaash' in process_sequence else -1
            li_index = process_sequence.index('Li_adsorption') if 'Li_adsorption' in process_sequence else -1
            if T_evap > T_desorp :
                E_water_evap = (((T_evap - T_desorp) * hCHH * water_evap_in) / 10 ** 6) * heat_loss

                if mg_index != -1 and li_index != -1 and mg_index < li_index :
                    E_adsorp_without_evap_water = (((T_adsorp - T_Mg_soda) * hCHH_bri * df_adsorption.iloc[
                        1,1]) / 10 ** 6) / heat_loss
                else :
                    E_adsorp_without_evap_water = (((T_adsorp - T_out) * hCHH_bri * df_adsorption.iloc[
                        1,1]) / 10 ** 6) / heat_loss

                E_adsorp_adapted = E_adsorp_without_evap_water - E_water_evap

                if E_adsorp_adapted < 0 :
                    E_adsorp_adapted = 0

            else :
                if mg_index != -1 and li_index != -1 and mg_index < li_index :
                    E_adsorp_adapted = ((((T_desorp - T_out) * hCHH * df_adsorption.iloc[3,1]) +
                                         ((T_adsorp - T_Mg_soda) * hCHH_bri * df_adsorption.iloc[
                                             1,1])) / 10 ** 6) / heat_loss
                else :
                    E_adsorp_adapted = ((((T_desorp - T_out) * hCHH * df_adsorption.iloc[3,1]) +
                                         ((T_adsorp - T_out) * hCHH_bri * df_adsorption.iloc[
                                             1,1])) / 10 ** 6) / heat_loss

            df_adsorption.loc[5,'Values'] = E_adsorp_adapted
            df_adsorption.loc[5,'per kg'] = E_adsorp_adapted / df_adsorption.iloc[0,1]

        else :
            E_adsorp_adapted = (((T_desorp - T_out) * hCHH * df_adsorption.iloc[3,1]) / 10 ** 6) / heat_loss
            df_adsorption.loc[5,'Values'] = E_adsorp_adapted
            df_adsorption.loc[5,'per kg'] = E_adsorp_adapted / df_adsorption.iloc[0,1]

        return df_adsorption,df_triple_evaporator

    def using_liquid_waste_for_adsorption_or_ion_exchanger(df_adsorption,df_centrifuge_TG,constants,params,
                                                           site_parameters) :
        T_desorp = params.get('T_desorp',constants['T_desorp'])
        T_Liprec = params.get('T_Liprec',constants['T_Liprec'])
        hCHH = params.get('hCHH',constants['hCHH'])
        heat_loss = params.get('heat_loss',constants['heat_loss'])
        waste_ratio = params.get('waste_ratio',constants['waste_ratio'])

        print('Using liquid waste from centrifuge_TG for adsorption or ion exchanger')
        print(f'Water saved due to re-circulation: {df_centrifuge_TG.iloc[3,1] / df_adsorption.iloc[3,1] * 100} %')

        try :
            liquid_waste_centrifuge_TG = df_centrifuge_TG.iloc[3,1]
            if liquid_waste_centrifuge_TG < 0 :
                liquid_waste_centrifuge_TG = -liquid_waste_centrifuge_TG
            print('Liquid waste from centrifuge_TG:',liquid_waste_centrifuge_TG)

            new_value = df_adsorption.iloc[3,1] - (1 - waste_ratio) * liquid_waste_centrifuge_TG
            print(new_value)

            if new_value >= 0 :
                new_value_kg = new_value / df_adsorption.iloc[0,1]
                df_adsorption.loc[3,'Values'] = new_value
                df_adsorption.loc[3,'per kg'] = new_value_kg
                print('Liquid waste from centrifuge_TG used for Li-adsorption')

                df_centrifuge_TG.loc[3,'Values'] = (waste_ratio * liquid_waste_centrifuge_TG)
                df_centrifuge_TG.loc[3,'per kg'] = (
                        (waste_ratio * liquid_waste_centrifuge_TG) / df_centrifuge_TG.iloc[0,1])

                if T_desorp > T_Liprec :
                    E_liquid_waste = (((T_desorp - T_Liprec) * hCHH * new_value) / 10 ** 6) * heat_loss
                    df_adsorption.loc[5,'Values'] = E_liquid_waste
                    df_adsorption.loc[5,'per kg'] = E_liquid_waste / df_adsorption.iloc[0,1]
                else :
                    print("No additional energy needed to heat up liquid waste")

            else :
                df_adsorption.loc[3,'Values'] = 0
                df_adsorption.loc[3,'per kg'] = 0
                df_centrifuge_TG.loc[3,'Values'] = -((-new_value) + (waste_ratio * liquid_waste_centrifuge_TG))

        except IndexError as e :
            print("Error: Index out of range. Please check the input dataframes.",e)
        except KeyError as e :
            print("Error: Missing required column or index in the dataframe.",e)
        except Exception as e :
            print("An unexpected error occurred:",e)

        return df_adsorption,df_centrifuge_TG


class CaMg_removal_sodiumhydrox:
    def execute(self, site_parameters, m_in, Ca_mass_leftover, constants, params):
        process_name = 'df_CaMg_removal_sodiumhydrox'
        vec_end = site_parameters['vec_end']
        deposit_type = site_parameters['deposit_type']

        # Use constant values
        Mg = constants['Mg']
        Ba = constants['Ba']
        Sr = constants['Sr']
        Na = constants['Na']
        O = constants['O']
        H = constants['H']
        Ca = constants['Ca']
        C = constants['C']

        # Use params if provided, otherwise fallback to constants
        left_over = params.get('Ca_left_over', constants['Ca_left_over'])
        quicklime_reaction_factor = params.get('quicklime_reaction_factor', constants['quicklime_reaction_factor'])
        sodiumhydroxide_reaction_factor = params.get('sodiumhydroxide_reaction_factor', constants['sodiumhydroxide_reaction_factor'])

        if Ca_mass_leftover is None:
            Ca_mass_leftover = 0

        Ca_mass = left_over * (vec_end[4] / 100 * m_in + Ca_mass_leftover)
        Mg_mass = left_over * vec_end[5] / 100 * m_in

        if deposit_type == "geothermal":
            Ba_mass = left_over * vec_end[-2] / 100 * m_in
            Sr_mass = left_over * vec_end[-3] / 100 * m_in
        else:
            Ba_mass = 0
            Sr_mass = 0

        NaOH = (Mg_mass / Mg + Ba_mass / Ba + Sr_mass / Sr) * 2 * (Na + O + H) * sodiumhydroxide_reaction_factor
        water_NaOH = NaOH / (Na + O + H) * (2 * H + O) * 1.2  # with process water

        sodaash_Ca = Ca_mass / Ca * (2 * Na + C + 3 * O)
        water_sodaash_Ca = sodaash_Ca / constants['sodaash_solution']  # with process water
        water_sum = water_sodaash_Ca + water_NaOH

        waste_MgBaSr = -((Mg_mass / Mg) * (Mg + 2 * (O + H)) + (Ba_mass / Ba) * (Ba + 2 * (O + H)) + (Sr_mass / Sr) * (
                Sr + 2 * (O + H)))
        waste_Ca = -(Ca_mass / Ca * (Ca + 3 * (C + O)))
        waste_sum = waste_MgBaSr + waste_Ca

        m_output = m_in + NaOH + water_NaOH + sodaash_Ca + water_sodaash_Ca + waste_MgBaSr + waste_Ca

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"NaOH_{process_name}",
                f"water_sum_{process_name}",
                f"chemical_sodaash_{process_name}",
                f"waste_solid_{process_name}"
            ],
            "Values": [
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
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': Ca_mass_leftover,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }



#Mg removal by soda ash
class Mg_removal_sodaash:
    def execute(self, site_parameters, m_in, constants, params):
        process_name = "df_Mg_removal_sodaash"
        vec_end = site_parameters['vec_end']
        vec_ini = site_parameters['vec_ini']
        second_Li_enrichment_reported = site_parameters['second_Li_enrichment_reported']
        second_Li_enrichment = site_parameters['second_Li_enrichment']
        T_out = site_parameters['annual_airtemp']
        motherliq_reported = site_parameters['motherliq_reported']


        # Use constant values
        Mg = constants['Mg']
        Na = constants['Na']
        C = constants['C']
        O = constants['O']
        Cl = constants['Cl']
        hCHH_bri = constants['hCHH_bri']

        # Use params if provided, otherwise fallback to constants
        sodaash_solution = params.get('sodaash_solution', constants['sodaash_solution'])
        T_Mg_soda = params.get('T_Mg_soda', constants['T_Mg_soda'])
        T_motherliq = params.get('T_motherliq', constants['T_motherliq'])
        heat_loss = params.get('heat_loss', constants['heat_loss'])
        sodaash_reaction_factor = params.get('sodaash_reaction_factor', constants['sodaash_reaction_factor'])
        motherliq_factor = params.get('motherliq_factor', constants['motherliq_factor'])

        if np.isnan(vec_end[5]):
            if second_Li_enrichment_reported == 1:
                Li_conc_factor = second_Li_enrichment / vec_ini[0]
                vec_end[5] = vec_ini[5] / Li_conc_factor
            else:
                Li_conc_factor = vec_end[0] / vec_ini[0]
                vec_end[5] = vec_ini[5] / Li_conc_factor

        sodaash_Mg = (((vec_end[5] / 100) * m_in) / Mg) * (Na * 2 + C + O * 3) * sodaash_reaction_factor
        water_soda_Mg = sodaash_Mg / sodaash_solution

        MgCO3_waste = ((vec_end[5] / 100) * m_in / Mg) * (Mg + C + O * 3)
        NaCl_waste = (2 * MgCO3_waste / (Mg + C + O * 3) * (Na + Cl))
        waste_sum = (MgCO3_waste + NaCl_waste)

        if motherliq_reported == 1:
            motherliq = motherliq_factor * m_in
            m_mixbri = m_in + motherliq
            T_mix = (motherliq * T_motherliq + T_Mg_soda * m_in) / m_mixbri

            if T_Mg_soda > T_mix:
                E_Mg = ((T_Mg_soda - T_mix) * hCHH_bri * m_mixbri / 10 ** 6) / heat_loss
            else:
                E_Mg = -((T_mix - T_Mg_soda) * hCHH_bri * m_mixbri / 10 ** 6)
        else:
            motherliq = 0
            m_mixbri = m_in
            if T_Mg_soda > T_out:
                E_Mg = ((T_Mg_soda - T_out) * hCHH_bri * m_mixbri / 10 ** 6) / heat_loss
            else:
                E_Mg = -((T_Mg_soda - T_out) * hCHH_bri * m_mixbri / 10 ** 6)

        if E_Mg < 0:
            energy_variable_name = f'waste_heat_{process_name}'
        else:
            energy_variable_name = f'E_{process_name}'

        m_output = m_mixbri + water_soda_Mg + sodaash_Mg

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                energy_variable_name,
                f"chemical_sodaash_{process_name}",
                f"water_sodaash_{process_name}",
                # f"waste_solid_{process_name}",
            ],
            "Values": [
                m_output,
                m_in,
                E_Mg,
                sodaash_Mg,
                water_soda_Mg,
                # waste_sum,
            ],
        }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': waste_sum,
            'waste_centrifuge_quicklime': None,
            'motherliq': motherliq,
            'water_NF': None
        }


#Mg removal by quicklime
class Mg_removal_quicklime :
    def execute(self,site_parameters,m_in,constants,params) :
        process_name = "df_Mg_removal_quicklime"

        # Use constant values
        Mg = constants['Mg']
        Ca = constants['Ca']
        O = constants['O']
        H = constants['H']
        S = constants['S']

        # Use params if provided, otherwise fallback to constants
        Mg_conc_pulp_quicklime = params.get('Mg_conc_pulp_quicklime',constants['Mg_conc_pulp_quicklime'])
        quicklime_reaction_factor = params.get('quicklime_reaction_factor',constants['quicklime_reaction_factor'])

        lime = (((Mg_conc_pulp_quicklime / 100) * m_in) / Mg) * (Ca + O * 2 + H * 2) * quicklime_reaction_factor
        water_lime = (lime / (Ca + O)) * (H * 2 + O)

        waste_Ca = (lime / (Ca + 2 * H + 2 * O)) * (0.66 * (S + Ca + O * 4 + 2 * (H * 2 + O)))
        waste_Mg = (lime / (Ca + 2 * H + 2 * O)) * (Mg + H * 2 + O * 2)
        waste_sum = waste_Ca + waste_Mg
        m_output = lime + water_lime + m_in

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"chemical_lime_{process_name}",
                f"water_lime_{process_name}",
                # f"waste_solid_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                lime,
                water_lime,
                # waste_sum,
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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : waste_sum,
            'motherliq' : None,
            'water_NF' : None
            }


class sulfate_removal_calciumchloride :
    def execute(self,site_parameters,m_in,constants,params) :
        process_name = "df_sulfate_removal_calciumchloride"

        # Use constant values
        S = constants['S']
        O = constants['O']
        Ca = constants['Ca']
        Cl = constants['Cl']

        # Use params if provided, otherwise fallback to constants
        calciumchloride_solution = params.get('calciumchloride_solution',constants['calciumchloride_solution'])

        vec_end = site_parameters['vec_end']

        prod_sulfate = ((((0.3 * vec_end[6] / 100) * m_in * 1000) / (S + O * 4)) * (Ca + S + O * 4)) / 1000

        waste_sulfate = -prod_sulfate  # Mass of precipitated anhydrite due to calcium chloride [kg]
        calciumchloride = 0.66 * (((((Ca / (Ca + S + O * 4)) * prod_sulfate * 1000) / Ca) * (
                Ca + Cl * 2)) / 1000)  # 0.3 because Tran and Luong (2015) stated 70 % sulfates already precipitated
        water_calciumchloride = calciumchloride / calciumchloride_solution  # assuming 30 wt. % CaCl2 solution
        m_output = m_in - waste_sulfate + water_calciumchloride  # Mass going out of this process [kg]

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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }


class ion_exchange_L:
    def __init__(self, custom_name=None):
        self.custom_name = custom_name

    def execute(self, site_parameters, m_in, water_evap, constants, params):
        process_name = self.custom_name if self.custom_name else "df_ion_exchange_L"

        # Retrieve parameters, falling back to constants if not provided
        elec_IX_factor = params.get('elec_IX_factor', constants['elec_IX_factor'])
        water_IX_factor = params.get('water_IX_factor', constants['water_IX_factor'])
        HCl_IX_factor = params.get('HCl_IX_factor', constants['HCl_IX_factor'])
        NaOH_IX_factor = params.get('NaOH_IX_factor', constants['NaOH_IX_factor'])
        heat_IX_factor = params.get('heat_IX_factor', constants['heat_IX_factor'])
        Cl_IX_factor = params.get('Cl_IX_factor', constants['Cl_IX_factor'])
        Na_IX_factor = params.get('Na_IX_factor', constants['Na_IX_factor'])

        # Calculate the required values
        elec_IX = elec_IX_factor * m_in  # Electricity demand for ion exchanger [kWh]
        water_IX = (water_IX_factor * m_in)*0.5  # Required mass of deionized water [kg]
        HCl_IX = HCl_IX_factor * m_in  # HCl demand for ion exchanger [kg]
        NaOH_IX = NaOH_IX_factor * m_in  # NaOH demand for ion exchanger [kg]
        heat_IX = heat_IX_factor * m_in  # Thermal energy waste for ion exchanger [MJ]
        Cl_IX = Cl_IX_factor * m_in  # Chlorine waste production [kg]
        Na_IX = Na_IX_factor * m_in  # Sodium waste production [kg]
        m_output = m_in

        # Create DataFrame with the results
        df_data = {
            "Variables": [
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
            "Values": [
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
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }

    def update_IX( df_ion_exchange_L, df_triple_evaporator):
        water_evap = df_triple_evaporator.iloc[-1, 1]
        new_value = df_ion_exchange_L.iloc[3, 1] - water_evap
        if new_value >= 0:
            df_ion_exchange_L.loc[3, 'Values'] = new_value
            new_value_kg = df_ion_exchange_L.iloc[3, 2] - (water_evap / df_ion_exchange_L.iloc[0, 1])
            df_ion_exchange_L.loc[3, 'per kg'] = new_value_kg
            print(f"There is no left-over of water after IX.")

        elif new_value < 0:
            df_ion_exchange_L.loc[3, 'Values'] = 0
            new_value_kg = 0
            df_ion_exchange_L.loc[3, 'per kg'] = new_value_kg
            print(f"There is left-over after IX ({new_value} kg).")
            pass

        return df_ion_exchange_L


#Ion exchanger - high water demand
class ion_exchange_H:
    def __init__(self, custom_name=None):
        self.custom_name = custom_name

    def execute(self, site_parameters, m_in, water_evap, constants, params):
        process_name = self.custom_name if self.custom_name else "df_ion_exchange_H"

        # Retrieve parameters, falling back to constants if not provided
        elec_IX_factor = params.get('elec_IX_factor', constants['elec_IX_factor']) * 3
        water_IX_factor = params.get('water_IX_factor', constants['water_IX_factor']) * 1.5
        HCl_IX_factor = params.get('HCl_IX_factor', constants['HCl_IX_factor']) * 3
        NaOH_IX_factor = params.get('NaOH_IX_factor', constants['NaOH_IX_factor']) * 3
        heat_IX_factor = params.get('heat_IX_factor', constants['heat_IX_factor']) * 3
        Cl_IX_factor = params.get('Cl_IX_factor', constants['Cl_IX_factor']) * 3
        Na_IX_factor = params.get('Na_IX_factor', constants['Na_IX_factor']) * 3

        # Calculate the required values
        elec_IX = elec_IX_factor * m_in  # Electricity demand for ion exchanger [kWh]
        water_IX = water_IX_factor * m_in  # Required mass of deionized water [kg]
        HCl_IX = HCl_IX_factor * m_in  # HCl demand for ion exchanger [kg]
        NaOH_IX = NaOH_IX_factor * m_in  # NaOH demand for ion exchanger [kg]
        heat_IX = heat_IX_factor * m_in  # Thermal energy demand for ion exchanger [MJ]
        Cl_IX = Cl_IX_factor * m_in  # Chlorine waste production [kg]
        Na_IX = Na_IX_factor * m_in  # Sodium waste production [kg]
        m_output = m_in

        # Create DataFrame with the results
        df_data = {
            "Variables": [
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
            "Values": [
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
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }

    def update_IX(df_ion_exchange_H, df_triple_evaporator):
        water_evap = df_triple_evaporator.iloc[-1, 1]
        new_value = df_ion_exchange_H.iloc[3, 1] - water_evap

        if new_value >= 0:
            df_ion_exchange_H.loc[3, "Values"] = new_value
            new_value_kg = df_ion_exchange_H.iloc[3]["per kg"] - (water_evap / df_ion_exchange_H.iloc[0, 1])
            df_ion_exchange_H.loc[3, "per kg"] = new_value_kg
            print(f"There is no left-over of water after IX.")

        elif new_value < 0:
            df_ion_exchange_H.loc[3, 'Values'] = 0
            new_value_kg = 0
            df_ion_exchange_H.loc[3, 'per kg'] = new_value_kg
            print(f"There is left-over after IX ({new_value} kg).")
            pass

        return df_ion_exchange_H


class nanofiltration:
    def execute(self, site_parameters, m_in, constants, params):
        process_name = 'df_nanofiltration'

        # Retrieve parameters, falling back to constants if not provided
        elec_nano_factor = params.get('elec_nano_factor', constants['elec_nano_factor'])
        m_output_factor = params.get('m_output_factor', constants['m_output_factor'])

        elec_nano = (elec_nano_factor * m_in) / 1000  # kWh, based on Li et al (2020)
        m_output = m_output_factor * m_in
        waterother = m_in - m_output

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"waterother_{process_name}"
            ],
            "Values": [
                m_output,
                m_in,
                elec_nano,
                waterother
            ],
        }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0][1]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': waterother
        }


class reverse_osmosis:
    def execute(self, site_parameters, m_in, constants, params):
        process_name = 'df_reverse_osmosis'

        # Retrieve parameters, falling back to constants if not provided
        elec_osmosis_factor = params.get('elec_osmosis_factor', constants['elec_osmosis_factor'])
        Li_in_RO = params.get('Li_in_RO', constants['Li_in_RO'])
        Li_out_RO = params.get('Li_out_RO', constants['Li_out_RO'])

        elec_osmosis = (elec_osmosis_factor * m_in / 1000)  # kWh, based on ecoinvent (2008)
        water_RO = (1 - (Li_in_RO / Li_out_RO)) * m_in
        m_output = Li_in_RO / Li_out_RO * m_in

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"waterother_{process_name}",
            ],
            "Values": [
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
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': water_RO,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }


class triple_evaporator :
    def execute(self,site_parameters,m_in,prod,motherliq,constants,params) :
        process_name = 'df_triple_evaporator'
        deposit_type = site_parameters['deposit_type']  # type of deposit

        # Retrieve parameters, falling back to constants if not provided
        E_evap_factor = params.get('E_evap_factor',constants['E_evap_factor'])
        elec_evap_factor = params.get('elec_evap_factor',constants['elec_evap_factor'])
        evaporator_steam_factor = params.get('evaporator_steam_factor',constants['evaporator_steam_factor'])

        # print("m_in:",m_in,"type:",type(m_in))
        # print("constants['dens_pulp']:",constants['dens_pulp'],"type:",type(constants['dens_pulp']))
        # print("E_evap_factor:",constants['E_evap_factor'],"type:",type(constants['E_evap_factor']))

        # For all sites, heat and power demand same calculation
        E_evap = (m_in / constants['dens_pulp']) * E_evap_factor  # MJ per m3 input
        elec_evap = (m_in / constants['dens_pulp']) * elec_evap_factor  # kWh per m3 input

        # Adaption to specific site and reported technology
        if deposit_type == 'geothermal' :
            Li_in_evaporator = constants['Li_in_RO']
            Li_out_evaporator = constants['Li_out_evaporator_geothermal']
            steam = ((Li_in_evaporator / Li_out_evaporator * m_in) / constants[
                'evaporator_gor']) * evaporator_steam_factor
            water_evap = (1 - (Li_in_evaporator / Li_out_evaporator)) * m_in
            m_output = Li_in_evaporator / Li_out_evaporator * m_in

        if deposit_type == 'salar' :
            if motherliq is not None and motherliq != 0 :
                m_output = motherliq + 1.5 * (
                            prod * (2 * constants['Li'] / (2 * constants['Li'] + constants['C'] + constants['O'] * 3)))
                water_evap = m_in - m_output
                steam = (water_evap / constants[
                    'evaporator_gor']) * evaporator_steam_factor  # 0.2 is there because we assume that the steam is recycled reducing the energy demand and so on
            else :
                Li_in_evaporator = (constants['Li_out_adsorb'] * 10e-4) / constants[
                    'dens_frw'] * 100  # 1650 mg/L in weight percent
                Li_out_evaporator = 0.9 * constants['Li_out_EP_DLE']
                steam = (((Li_in_evaporator / Li_out_evaporator * m_in) / constants[
                    'evaporator_gor'])) * evaporator_steam_factor
                water_evap = (1 - (Li_in_evaporator / Li_out_evaporator)) * m_in
                m_output = m_in / (
                            Li_out_evaporator / Li_in_evaporator)  # (Li_in_evaporator * m_in) / Li_out_evaporator #(Li_in_evaporator / Li_out_evaporator * m_in)

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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }

    def update_triple_evaporator(df_triple_evaporator, site_parameters, constants, params):
        T_out = site_parameters['annual_airtemp']  # annual air temperature
        ratio_T = 1 - ((params.get('T_evap', constants['T_evap']) - params.get('T_desorp', constants['T_desorp'])) / (
            params.get('T_evap', constants['T_evap']) - T_out))  # Temperature ratio when pulp is already heated
        new_value_E = df_triple_evaporator.iloc[2,1] * ratio_T
        new_value_E_kg = df_triple_evaporator.iloc[2,2] * ratio_T

        # Update values in df_triple_evaporator
        df_triple_evaporator.loc[2,'Values'] = new_value_E
        df_triple_evaporator.loc[2,'per kg'] = new_value_E_kg

        return df_triple_evaporator


class Liprec_TG :
    def execute(self,prod,site_parameters,m_in,constants,params) :
        process_name = 'df_Liprec_TG'
        T_out = site_parameters['annual_airtemp']  # annual air temperature

        # Retrieve parameters, falling back to constants if not provided
        T_Liprec = params.get('T_Liprec',constants['T_Liprec'])
        hCHH_bri = constants['hCHH_bri']
        heat_loss = params.get('heat_loss',constants['heat_loss'])
        Li = constants['Li']
        C = constants['C']
        O = constants['O']
        Na = constants['Na']
        Cl = constants['Cl']

        sodaash_solution = params.get('sodaash_solution',constants['sodaash_solution'])
        sodaash_reaction_factor = params.get('sodaash_reaction_factor',constants['sodaash_reaction_factor'])

        E_Liprec = (((T_Liprec - T_out) * hCHH_bri * m_in) / 10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        sodaash_Liprec = ((prod * 1000 / (Li * 2 + C + O * 3)) * (
                    Na * 2 + C + O * 3) / 1000) * sodaash_reaction_factor  # stoichiometrically calculated soda ash demand [kg]
        prod_NaCl2 = (prod * 1000 / (Li * 2 + C + O * 3)) * (
                    Na + Cl) / 1000   # waste production [kg]
        water_sodaash = sodaash_Liprec / sodaash_solution  # water demand to produce Na2CO3 solution [kg]
        m_output = m_in + sodaash_Liprec + water_sodaash  # output of lithium carbonate precipitation process [kg]

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"E_{process_name}",
                f"chemical_sodaash_{process_name}",
                f"water_{process_name}",
                ],
            "Values" : [
                m_output,
                m_in,
                E_Liprec,
                sodaash_Liprec,
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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }


class dissolution:
    def execute(self, prod, site_parameters, m_in, constants, params):
        process_name = "df_dissolution"

        # Retrieve parameters, falling back to constants if not provided
        Li = constants['Li']
        C = constants['C']
        O = constants['O']
        H = constants['H']
        dissol_cons = params.get('dissol_cons', constants['dissol_cons'])
        CO2_factor = params.get('CO2_factor', constants['CO2_factor'])

        prod_libicarb = prod / (Li * 2 + C + O * 3) * (2 * (Li + H + C + O * 3))  # mass of lithiumbicarbonate [kg]
        mass_HCO = prod_libicarb * (H * 2 + C + O * 3) / (Li + H + C + O * 3)  # mass of required HCO3- in solution [kg]
        mass_CO2 = (((C + O * 2) / (H * 2 + C + O * 3)) * mass_HCO) * CO2_factor  # mass of required CO2 to dissolve lithium carbonate [kg]
        water_deion2 = (prod / dissol_cons)  # Required mass of deionized water to dissolve lithium carbonate [kg]
        elec_dissol = 0
        m_output = m_in + water_deion2  # Mass output of dissolution process [kg]

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"water_{process_name}",
                f"elec_{process_name}",
            ],
            "Values": [
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
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': mass_CO2,
            'prod_libicarb': prod_libicarb,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }



class Liprec_BG:
    def execute(self, mass_CO2, prod_libicarb, prod, site_parameters, m_in, constants, params):
        process_name = 'df_Liprec_BG'
        technology_group = site_parameters['technology_group']
        boil_point = site_parameters['boilingpoint_process']  # boiling point
        T_out = site_parameters['annual_airtemp']  # annual air temperature

        # Retrieve constants
        Li = constants['Li']
        C = constants['C']
        O = constants['O']
        H = constants['H']
        hCC = constants['hCC']
        hCH = constants['hCH']
        latheat_H = constants['latheat_H']
        hCHH = constants['hCHH']
        heat_loss = constants['heat_loss']
        T_IX = params.get('T_IX', constants['T_IX'])

        rel_heat_CO2 = mass_CO2 * hCC * (boil_point - T_out)  # heat loss due to CO2 release [J]
        rel_heat_H2O = (
            (H * 2 + O) / (2 * (Li + H + C + O * 3))) * prod_libicarb * hCH * (boil_point - T_out) + (
            (H * 2 + O) / (2 * (Li + H + C + O * 3))) * prod_libicarb * latheat_H  # heat loss due to H2O release [J]
        waste_heat_sum = -(rel_heat_CO2 + rel_heat_H2O) / 10 ** 6  # waste heat [MJ]

        if technology_group == "salar_IX":
            E_seclicarb = (((boil_point - T_IX) * hCHH * m_in + rel_heat_CO2 + rel_heat_H2O) /
                           10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        else:
            E_seclicarb = (((boil_point - T_out) * hCHH * m_in + rel_heat_CO2 + rel_heat_H2O) /
                           10 ** 6) / heat_loss  # Thermal energy demand [MJ]

        mass_h2o = -((H * 2 + O) / (2 * (Li + H + C + O * 3))) * prod_libicarb  # Mass of H2O lost due to precipitation of Li2CO3 [kg]
        m_output = m_in + mass_h2o + prod - mass_CO2  # Output mass of this process [kg]

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"waste_heat_{process_name}",
                f"E_{process_name}"
            ],
            "Values": [
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
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }



# Washing Li2CO3 (TG)
class washing_TG:
    def execute(self, prod, site_parameters, m_in, constants, params):
        process_name = 'df_washing_TG'

        # Retrieve constants
        hCHH = constants['hCHH']
        heat_loss = constants['heat_loss']

        T_out = site_parameters['annual_airtemp']  # annual air temperature
        boil_point = site_parameters['boilingpoint_process']  # boiling point
        washing_factor = params.get('washing_factor', constants['washing_factor'])

        water_deion = washing_factor * prod  # Mass of water required for washing [kg]
        E_deion = (((boil_point - T_out) * hCHH * water_deion) / 10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        m_output = (1.75 * washing_factor) * prod  # Mass output of this process [kg]

        df_data = {
            "Variables": [f"m_output_{process_name}", f"m_in_{process_name}", f"water_{process_name}",
                          f"E_{process_name}"],
            "Values": [m_output, m_in, water_deion, E_deion],
        }

        df_process = pd.DataFrame(df_data)
        df_process[f"per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }



# Washing Li2CO3 (BG)
class washing_BG:
    def execute(self, prod, site_parameters, m_in, constants, params):
        process_name = 'df_washing_BG'

        # Retrieve constants
        hCHH = constants['hCHH']
        heat_loss = constants['heat_loss']

        T_out = site_parameters['annual_airtemp']  # annual air temperature
        boil_point = site_parameters['boilingpoint_process']  # boiling point
        washing_factor = params.get('washing_factor', constants['washing_factor'])

        water_deion = washing_factor * prod  # Mass of water required for washing [kg]
        E_deion = (((boil_point - T_out) * hCHH * water_deion) / 10 ** 6) / heat_loss  # Thermal energy demand [MJ]
        m_output = (1.75 * washing_factor) * prod  # Mass output of this process [kg]

        df_data = {
            "Variables": [f"m_output_{process_name}", f"m_in_{process_name}", f"water_{process_name}",
                          f"E_{process_name}"],
            "Values": [m_output, m_in, water_deion, E_deion],
        }

        df_process = pd.DataFrame(df_data)
        df_process[f"per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }




class CentrifugeBase:
    def __init__(self, process_name, density_key, constants, params, prod_factor_key=None, waste_liquid_factor_key=None, waste_solid_factor_key=None, recycle_factor_key=None):
        self.process_name = process_name
        self.density_key = density_key
        self.constants = constants
        self.params = params
        self.prod_factor_key = prod_factor_key
        self.waste_liquid_factor_key = waste_liquid_factor_key
        self.waste_solid_factor_key = waste_solid_factor_key
        self.recycle_factor_key = recycle_factor_key

    def execute(self, prod, site_parameters, m_in, motherliq=None, constants=None, params=None):
        print(f"Executing {self.process_name} with params: {self.params}")
        density_pulp = site_parameters[self.density_key]
        elec_centri = 1.3 * m_in / (density_pulp * 1000)

        prod_factor = self.params.get(self.prod_factor_key, self.constants[self.prod_factor_key]) if self.prod_factor_key else None
        waste_liquid_factor = None
        waste_solid_factor = self.params.get(self.waste_solid_factor_key, self.constants[self.waste_solid_factor_key]) if self.waste_solid_factor_key else None
        recycle_factor = None

        m_output = prod_factor * prod if prod_factor is not None else m_in - (waste_liquid_factor * m_in if waste_liquid_factor else 0)

        waste_liquid, waste_solid, recycled_waste = 0, 0, 0

        if motherliq is not None:
            recycled_waste = motherliq
            waste_liquid = (m_in - motherliq - m_output)
        else:
            waste_liquid = (m_in - m_output)

        if waste_solid_factor is not None:
            waste_solid = (m_in - m_output) * waste_solid_factor



        variables = ['m_output', 'm_in', 'elec']
        values = [m_output, m_in, elec_centri]

        if waste_liquid:
            variables.append('waste_liquid')
            values.append(waste_liquid)
        if waste_solid:
            variables.append('waste_solid')
            values.append(waste_solid)
        if recycled_waste:
            variables.append('recycled_waste')
            values.append(recycled_waste)



        df_data = {
            "Variables": [f"{var}_{self.process_name}" for var in variables],
            "Values": values
        }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        return {
            'process_name': self.process_name,
            'm_out': m_output,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': motherliq,
            'water_NF': None
        }

class CentrifugeTG(CentrifugeBase):
    def __init__(self, constants, params):
        super().__init__(
            process_name='df_centrifuge_TG',
            density_key='density_brine',
            constants=constants,
            params=params,
            prod_factor_key='centrifuge_TG_prod_factor',
            waste_liquid_factor_key='centrifuge_TG_waste_liquid_factor',
            recycle_factor_key='centrifuge_TG_recycle_factor'
        )

class CentrifugeBG(CentrifugeBase):
    def __init__(self, constants, params):
        super().__init__(
            process_name='df_centrifuge_BG',
            density_key='density_brine',
            constants=constants,
            params=params,
            prod_factor_key='centrifuge_BG_prod_factor',
            waste_liquid_factor_key='centrifuge_BG_waste_liquid_factor'
        )

class CentrifugeWash(CentrifugeBase):
    def __init__(self, constants, params):
        super().__init__(
            process_name='df_centrifuge_wash',
            density_key='density_brine',
            constants=constants,
            params=params,
            prod_factor_key='centrifuge_wash_prod_factor',
            waste_liquid_factor_key='centrifuge_wash_waste_liquid_factor'
        )





class CentrifugePurification:
    def __init__(self, constants, params, waste_name, custom_name=None):
        if not isinstance(waste_name, str) or not waste_name.strip():
            raise ValueError("waste_name must be a non-empty string")
        self.process_name = custom_name if custom_name else f'df_centrifuge_purification_{waste_name.strip().lower()}'
        self.constants = constants
        self.params = params

    def execute(self, waste, m_in):
        process_name = self.process_name if self.process_name else f"df_centrifuge_purification_{waste.strip().lower()}"

        # Get the electricity factor from params or constants
        print(f'Electricity param: {self.params.get("centrifuge_electricity", self.constants["centrifuge_electricity"])}')
        elec_factor = 0.01
        elec_centri = waste * elec_factor
        m_output = m_in - waste

        # Compile data for dataframe
        variables = ['m_output', 'm_in', 'elec', 'waste_solid']
        values = [m_output, m_in, elec_centri, (-waste)]

        df_data = pd.DataFrame({
            "Variables": [f"{var}_{self.process_name}" for var in variables],
            "Values": values
        })
        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        # Return results in a dictionary
        return {
            'process_name': self.process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }

class CentrifugeSoda(CentrifugePurification):
    def __init__(self, constants, params):
        super().__init__(constants=constants, params=params, waste_name="sodaash")

class CentrifugeQuicklime(CentrifugePurification):
    def __init__(self, constants, params):
        super().__init__(constants=constants, params=params, waste_name="quicklime")

class Centrifuge_general(CentrifugePurification):
    def __init__(self, constants, params, custom_name):
        super().__init__(constants=constants, params=params, waste_name="general", custom_name=custom_name)




# Belt filter
class belt_filter:
    def execute(self, prod, site_parameters, m_in, constants, params):
        process_name = "belt_filter"

        # Retrieve constants and parameters
        dens_H2O = constants['dens_H2O']
        dens_Licarb = constants['dens_Licarb']
        elec_belt_factor = params.get('beltfilter_electricity', constants['beltfilter_electricity'])

        recyc_water = m_in - 1.5 * prod  # No waste is produced because the residual is sent back
        elec_belt = elec_belt_factor * (
                ((m_in - 1.5 * prod) / dens_H2O) + (1.5 * prod / dens_Licarb)
        )  # Electricity consumption of centrifuge [kWh]
        m_output = 1.5 * prod

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"elec_{process_name}",
                f"recyc_water_{process_name}",
            ],
            "Values": [
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
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }


# Rotary dryer
class rotary_dryer :
    def execute(self, prod, site_parameters, m_in, constants, params) :
        process_name = "df_rotary_dryer"

        # Retrieve constants and parameters
        heat_loss = constants['heat_loss']
        rotarydryer_heat = params.get('rotarydryer_heat', constants['rotarydryer_heat'])
        rotarydryer_electricity = params.get('rotarydryer_electricity', constants['rotarydryer_electricity'])
        rotarydryer_waste_heat = params.get('rotarydryer_waste_heat', constants['rotarydryer_waste_heat'])

        E_dry = (rotarydryer_heat * prod * 7) / heat_loss  # Thermal energy demand [MJ]
        elec_dry = rotarydryer_electricity * prod * 0.3  # Electricity demand [kWh]
        waste_heat = - rotarydryer_waste_heat * E_dry  # Waste heat [MJ]
        m_output = prod

        df_data = {
            "Variables" : [
                f"m_output_{process_name}",
                f"m_in_{process_name}",
                f"E_{process_name}",
                f"elec_{process_name}",
                f"waste_heat_{process_name}"
                ],
            "Values" : [
                m_output,
                m_in,
                E_dry,
                elec_dry,
                waste_heat
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
            'waste_centrifuge_Boron' : None,
            'waste_centrifuge_sodaash' : None,
            'waste_centrifuge_quicklime' : None,
            'motherliq' : None,
            'water_NF' : None
            }



# Water purification
class water_purification:
    def __init__(self, constants, params):
        self.constants = constants
        self.params = params

    def execute(self, site_parameters, water):
        process_name = "purification"

        # Retrieve constants and parameters
        water_purification_waste_factor = self.params.get('water_purification_waste_factor', self.constants['water_purification_waste_factor'])
        water_purification_new_factor = self.params.get('water_purification_new_factor', self.constants['water_purification_new_factor'])
        water_purification_elec_factor = self.params.get('water_purification_elec_factor', self.constants['water_purification_elec_factor'])

        waste = water * water_purification_waste_factor
        water_new = water * water_purification_new_factor
        elec_purification = (water_purification_elec_factor * water / 1000)
        m_output = water

        df_data = {
            "Variables": [
                f"m_output_{process_name}",
                f"water_{process_name}",
                f"waste_{process_name}",
                f"elec_purification_{process_name}",
            ],
            "Values": [
                m_output,
                water,
                waste,
                elec_purification,
            ],
        }

        df_process = pd.DataFrame(df_data)
        df_process["per kg"] = df_process["Values"] / df_process.iloc[0]["Values"]

        m_out = df_process.iloc[0]["Values"]

        return {
            'process_name': process_name,
            'm_out': m_out,
            'data_frame': df_process,
            'mass_CO2': None,
            'prod_libicarb': None,
            'water_RO': None,
            'water_evap': None,
            'Ca_mass_brine': None,
            'waste_centrifuge_Boron': None,
            'waste_centrifuge_sodaash': None,
            'waste_centrifuge_quicklime': None,
            'motherliq': None,
            'water_NF': None
        }


# Set up of the site - brine volumes and Li2CO3 production

def setup_site(eff, site_parameters, constants, params=None):
    if params is None:
        params = {}

    vec_ini = site_parameters['vec_ini']  # vector of concentrations at the beginning of the process sequence
    print('vec_ini in setup_site', vec_ini)
    Li_conc = vec_ini[0]  # concentration of lithium in the brine

    Dens_ini = site_parameters['density_brine']  # initial density of brine
    v_pumpbrs = site_parameters['brine_vol']  # volume of brine pumped per second
    op_days = site_parameters['operating_days']  # number of operating days per year
    prod_year = site_parameters['production']
    print('literature production ', prod_year)

    if eff == site_parameters['Li_efficiency']:  # if eff is not provided, then use the range of efficiencies
        eff = site_parameters['Li_efficiency']
    else:
        eff = eff  # efficiency of lithium extraction
        site_parameters['Li_efficiency'] = eff

    # Check if brine_vol is not provided and calculate it using production and Li_conc
    if pd.isna(v_pumpbrs):
        Li = constants['Li']
        C = constants['C']
        O = constants['O']
        v_pumpbrs = (prod_year * (2 * Li) / (2 * Li + C + O * 3)) / (
                op_days * 24 * 60 * 60 * (1000 * Dens_ini) * (Li_conc / 100)) * (1 / eff) * 1000
        site_parameters['brine_vol'] = v_pumpbrs  # Convert m³/s to L/s

    # Mass of brine going into the process sequence
    v_pumpbr = ((v_pumpbrs / 1000) * op_days * 60 * 60 * 24)  # volume of brine [m3/yr]
    m_pumpbr = v_pumpbr * Dens_ini * 1000  # mass of pumped brine per year [kg/yr]
    if pd.isna(prod_year):
        prod_year = (((v_pumpbrs / 1000) * op_days * 24 * 60 * 60 * (1000 * Dens_ini) * (Li_conc / 100)) / (
                (2 * Li) / (2 * Li + C + O * 3))) * eff
    print('Brine vol ', v_pumpbrs)
    print('Brine mass ', m_pumpbr)
    print('Production prod_year ', prod_year)

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
class ProcessManager:
    def __init__(self, site_parameters, m_in, prod_initial, process_sequence, filename, constants, params):
        setup_logging(filename + ".txt")
        self.site_parameters = site_parameters
        self.data_frames = {}
        self.m_in = m_in
        self.prod = prod_initial
        self.dynamic_attributes = {}
        self.process_sequence = process_sequence
        self.process_dependencies = {
            'Liprec_BG': ['dissolution'],
            'CentrifugeSoda': ['Mg_removal_sodaash'],
            'CentrifugeQuicklime': ['Mg_removal_quicklime']
        }
        self.keys_not_to_overwrite = ["Ca_mass_brine", "water_RO", "water_evap", "motherliq", "mass_CO2", "prod_libicarb", "water_NF"]
        self.logger = logging.getLogger('ProcessManager')
        self.log_folder = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/data/logging_files"
        self.constants = constants
        self.params = params if params else {}
        print(self.params)

    def _check_dependencies(self, current_process_base_name, executed_processes):
        dependencies = self.process_dependencies.get(current_process_base_name, [])
        for dependency in dependencies:
            dependency_pattern = dependency + '_'
            dependency_satisfied = any(
                proc.startswith(dependency_pattern) or proc == dependency for proc in executed_processes
            )
            if not dependency_satisfied:
                raise Exception(f"Dependency {dependency} for {current_process_base_name} has not been executed yet!")

    def _get_args_for_process(self,process_instance) :
        process_type = type(process_instance)
        print(self.params)

        if process_type == SiFeRemovalLimestone :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == MnZn_removal_lime :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == acidification :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == Li_adsorption :
            return (self.prod,self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == CaMg_removal_sodiumhydrox :
            Ca_mass_input = self.dynamic_attributes.get("Ca_mass_brine",None)
            return (self.site_parameters,self.m_in,Ca_mass_input,self.constants,self.params)
        elif process_type in [ion_exchange_L,ion_exchange_H] :
            water_evap_value = self.dynamic_attributes.get("water_evap",None)
            return (self.site_parameters,self.m_in,water_evap_value,self.constants,self.params)
        elif process_type == reverse_osmosis :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == triple_evaporator :
            motherliq_value = self.dynamic_attributes.get("motherliq",None)
            return (self.site_parameters,self.m_in,self.prod,motherliq_value,self.constants,self.params)
        elif process_type in [Liprec_TG,dissolution,washing_TG,washing_BG,belt_filter,rotary_dryer] :
            return (self.prod,self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == Liprec_BG :
            return (
            self.dynamic_attributes["mass_CO2"],self.dynamic_attributes["prod_libicarb"],self.prod,self.site_parameters,
            self.m_in,self.constants,self.params)
        elif process_type == CentrifugeTG :
            motherliq_value = self.dynamic_attributes.get("motherliq",None)
            return (self.prod,self.site_parameters,self.m_in,motherliq_value)
        elif process_type in [CentrifugeBG,CentrifugeWash] :
            return (self.prod,self.site_parameters,self.m_in)
        elif process_type == evaporation_ponds :
            return (self.site_parameters,self.m_in,self.prod,self.constants,self.params)
        elif process_type == B_removal_organicsolvent :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == transport_brine :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == sulfate_removal_calciumchloride :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == Mg_removal_sodaash :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == Mg_removal_quicklime :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == CentrifugeSoda :
            return (self.dynamic_attributes.get("waste_centrifuge_sodaash",None),self.m_in)
        elif process_type == CentrifugeQuicklime :
            return (self.dynamic_attributes.get("waste_centrifuge_quicklime",None),self.m_in)
        elif process_type == Centrifuge_general :
            return (0.05 * self.m_in,self.m_in)
        elif process_type == DLE_evaporation_ponds :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        elif process_type == nanofiltration :
            return (self.site_parameters,self.m_in,self.constants,self.params)
        else :
            raise ValueError(f"Unsupported process: {process_type}")

    def run(self, filename):
        setup_logging(filename)

        results = {}
        executed_processes = set()
        process_counts = {}

        for process_instance in self.process_sequence:
            process_name = type(process_instance).__name__
            custom_name = getattr(process_instance, 'custom_name', None)

            if custom_name:
                # Use the custom name directly if provided
                unique_process_name = custom_name
            else:
                # Increment and use count for unique naming if no custom name is provided
                process_counts[process_name] = process_counts.get(process_name, 0) + 1
                unique_process_name = f"{process_name}_{process_counts[process_name]}"

            updated_args = self._get_args_for_process(process_instance)
            #print(f"Arguments for {unique_process_name}: {updated_args}")

            self.logger.info(f"Arguments for {unique_process_name}: {updated_args}")

            self._check_dependencies(process_name, executed_processes)

            try:
                logging.info(f"Executing {process_name}")

                result = process_instance.execute(*updated_args)  # Unpack the updated_args

                # Log the dataframes (results) after the process has been executed
                if 'data_frame' in result:
                    self.logger.info(f"Dataframe for {process_name}: {result['data_frame']}")

                for key, value in result.items():
                    if key != 'm_out' and key != 'data_frame':
                        # If the key is in keys_not_to_overwrite, handle its special logic
                        if key in self.keys_not_to_overwrite:
                            # If key already has a non-None value in dynamic_attributes, skip
                            if self.dynamic_attributes.get(value) is not None:
                                continue
                            # If the new value is None, skip
                            elif value is None:
                                continue
                        self.dynamic_attributes[key] = value

                self.m_in = result['m_out']
                results[unique_process_name] = result['data_frame']
                self.data_frames[unique_process_name] = result['data_frame']
                executed_processes.add(unique_process_name)

            except Exception as e:
                logging.error(f"Error in {unique_process_name}: {str(e)}")
                raise e

        if 'Li_adsorption_1' in self.data_frames and (
                'reverse_osmosis_1' in self.data_frames and 'triple_evaporator_1' in self.data_frames) :
            self.data_frames['Li_adsorption_1'],self.data_frames['reverse_osmosis_1'],self.data_frames[
                'triple_evaporator_1'] = Li_adsorption.update_adsorption_RO_evaporator(
                self.data_frames['Li_adsorption_1'],self.dynamic_attributes["water_RO"],
                self.dynamic_attributes['water_evap'],self.data_frames['reverse_osmosis_1'],
                self.data_frames['triple_evaporator_1'],self.constants,self.params,self.site_parameters)

        if 'Li_adsorption_1' in self.data_frames and 'nanofiltration_1' in self.data_frames \
                and 'reverse_osmosis_1' in self.data_frames :
            self.data_frames['Li_adsorption_1'],self.data_frames['nanofiltration_1'],self.data_frames[
                'reverse_osmosis_1'] = Li_adsorption.update_adsorption_nanofiltration_RO(
                self.data_frames['Li_adsorption_1'],self.dynamic_attributes['water_NF'],
                self.dynamic_attributes['water_RO'],
                self.data_frames['nanofiltration_1'],self.data_frames['reverse_osmosis_1'],self.constants,self.params,
                self.site_parameters)

            print('Updated Li_adsorption, nanofiltration and reverse osmosis.')

        if 'Li_adsorption_1' in self.data_frames and 'triple_evaporator_1' in self.data_frames \
                and not 'reverse_osmosis_1' in self.data_frames :
            self.data_frames['Li_adsorption_1'],self.data_frames[
                'triple_evaporator_1'] = Li_adsorption.update_adsorption_evaporator(
                self.data_frames['Li_adsorption_1'],self.dynamic_attributes['water_evap'],
                self.data_frames['triple_evaporator_1'],self.constants,self.params,self.site_parameters)

        if 'Li_adsorption_1' in self.data_frames and 'triple_evaporator_1' in self.data_frames \
                and not 'reverse_osmosis_1' in self.data_frames :
            self.data_frames['triple_evaporator_1'] = triple_evaporator.update_triple_evaporator(
                self.data_frames['triple_evaporator_1'],self.site_parameters,self.constants,self.params)

            print(f"Updated triple evaporator and Li_adsorption.")

        if 'ion_exchange_L_1' in self.data_frames and 'triple_evaporator_1' in self.data_frames \
                and not 'Li_adsorption_1' in self.data_frames :
            self.data_frames['ion_exchange_L_1'] = ion_exchange_L.update_IX(self.data_frames['ion_exchange_L_1'],
                                                                            self.data_frames['triple_evaporator_1'])



        if 'ion_exchange_H_1' in self.data_frames and 'triple_evaporator_1' in self.data_frames \
                and not 'Li_adsorption_1' in self.data_frames :
            self.data_frames['ion_exchange_H_1'] = ion_exchange_H.update_IX(self.data_frames['ion_exchange_H_1'],
                                                                            self.data_frames['triple_evaporator_1'])

        if 'Li_adsorption_1' in self.data_frames and 'CentrifugeTG_1' in self.data_frames :
            self.data_frames['Li_adsorption_1'],self.data_frames[
                'CentrifugeTG_1'] = Li_adsorption.using_liquid_waste_for_adsorption_or_ion_exchanger(
                self.data_frames['Li_adsorption_1'],self.data_frames['CentrifugeTG_1'],self.constants,self.params,
                self.site_parameters)

        return results

    def run_simulation(self,op_location,abbrev_loc,process_sequence,max_eff,
                       min_eff,eff_steps,Li_conc_steps,Li_conc_max,Li_conc_min,constants,params) :
        # print(f"run simulation: {abbrev_loc}")
        eff_range = np.arange(max_eff,min_eff - eff_steps + 0.001,-eff_steps)

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

                initial_data = extract_data(op_location,abbrev_loc,Li)

                prod,m_pumpbr = setup_site(eff,initial_data[abbrev_loc], constants, params = None)


                manager = ProcessManager(initial_data[abbrev_loc],m_pumpbr,prod,process_sequence,filename,constants,
                                         params = None)

                result_df = manager.run(filename)

                calculator = ResourceCalculator(result_df)
                results = calculator.calculate_resource_per_prod_mass(production_mass=prod)  # example production mass
                calculator.save_to_csv(results,
                                       filename=f'C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\results\\rawdata\\ResourceCalculator\\output_{abbrev_loc}.csv')

                results_dict[eff][Li] = {
                    'data_frames' : result_df
                    }

        base_directory = f'C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\results\\figures\\results_{abbrev_loc}'

        # Check if the base directory exists, if not create it
        if not os.path.exists(base_directory) :
            os.makedirs(base_directory)

        # Create a new directory for the specific location
        location_directory = os.path.join(base_directory,f'{abbrev_loc}_LCI')
        if not os.path.exists(location_directory) :
            os.makedirs(location_directory)

        # Path for the .pkl file
        file_path = os.path.join(location_directory,f"results_dict_{abbrev_loc}_{Li}_{eff}.pkl")

        with open(file_path,"wb") as f :
            pickle.dump(results_dict,f)

        print("Simulation completed and results stored in the dictionary.")

        #viz = Visualization()
        #viz.plot_resources_per_kg(results_dict,abbrev_loc)

        return results_dict,eff_range,Li_conc_range

    def run_simulation_with_literature_data(self,op_location,abbrev_loc,process_sequence,site_parameters,constants,
                                            params) :
        """
        Run the simulation with specific literature values for efficiency and lithium concentration.

        Parameters:
        - op_location: Operating location
        - abbrev_loc: Abbreviation for location
        - process_sequence: Sequence of processes
        - literature_eff: Efficiency value from literature
        - literature_Li_conc: Lithium concentration value from literature
        """
        vec_ini = site_parameters['vec_ini']  # vector of concentrations at the beginning
        literature_Li_conc = vec_ini[0]  # concentration of lithium in the brine
        print(f'Run simulation with literature data: {literature_Li_conc}')
        literature_eff = site_parameters['Li_efficiency']  # efficiency of lithium extraction

        results_dict = {}

        # Ensure the nested dictionary for each efficiency exists
        if literature_eff not in results_dict :
            results_dict[literature_eff] = {}

        filename = f"{abbrev_loc}_eff{literature_eff}_Li{literature_Li_conc}.txt"

        initial_data = extract_data(op_location,abbrev_loc,literature_Li_conc)


        prod,m_pumpbr = setup_site(literature_eff,initial_data[abbrev_loc], constants, params = None)

        manager = ProcessManager(initial_data[abbrev_loc],m_pumpbr,prod,process_sequence,filename,constants,params = None)

        result_df = manager.run(filename)

        calculator = ResourceCalculator(result_df)
        results = calculator.calculate_resource_per_prod_mass(production_mass=prod)  # example production mass
        calculator.save_to_csv(results,
                               filename=f'C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\results\\rawdata\\ResourceCalculator\\output_{abbrev_loc}.csv')

        results_dict[literature_eff][literature_Li_conc] = {
            'data_frames' : result_df
            }

        base_directory = f'C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\results\\figures\\results_{abbrev_loc}'

        # Check if the base directory exists, if not create it
        if not os.path.exists(base_directory) :
            os.makedirs(base_directory)

        # Create a new directory for the specific location
        location_directory = os.path.join(base_directory,f'{abbrev_loc}_LCI')
        if not os.path.exists(location_directory) :
            os.makedirs(location_directory)

        # Path for the .pkl file
        file_path = os.path.join(location_directory,
                                 f"results_dict_{abbrev_loc}_{literature_Li_conc}_{literature_eff}.pkl")

        with open(file_path,"wb") as f :
            pickle.dump(results_dict,f)

        print("Simulation completed and results stored in the dictionary.")

        return results_dict,literature_eff,literature_Li_conc


    def run_simulation_with_brinechemistry_data(self,site_name,abbrev_loc,process_sequence,site_data,
                                                constants, params) :
        initial_data = site_data
        literature_eff = initial_data['Li_efficiency']
        literature_Li_conc = initial_data['vec_ini'][0]

        results_dict = {}
        if literature_eff not in results_dict :
            results_dict[literature_eff] = {}

        filename = f"{abbrev_loc}_eff{literature_eff}_Li{literature_Li_conc}.txt"
        prod,m_pumpbr = setup_site(literature_eff,initial_data,constants)
        manager = ProcessManager(initial_data,m_pumpbr,prod,process_sequence,filename,constants,params=None)

        result_df = manager.run(filename)

        results_dict[literature_eff][literature_Li_conc] = {
            'data_frames' : result_df
            }

        return results_dict, literature_eff, literature_Li_conc

    def run_simulation_with_brinechemistry_data_old(self,op_location,abbrev_loc,process_sequence,site_parameters,constants,
                                            params) :
        """
        Run the simulation with specific literature values for efficiency and lithium concentration.

        Parameters:
        - op_location: Operating location
        - abbrev_loc: Abbreviation for location
        - process_sequence: Sequence of processes
        - literature_eff: Efficiency value from literature
        - literature_Li_conc: Lithium concentration value from literature
        """
        vec_ini = site_parameters['vec_ini']  # vector of concentrations at the beginning
        literature_Li_conc = vec_ini[0]  # concentration of lithium in the brine
        print(f'Run simulation with literature data: {literature_Li_conc}')
        literature_eff = site_parameters['Li_efficiency']  # efficiency of lithium extraction

        results_dict = {}

        # Ensure the nested dictionary for each efficiency exists
        if literature_eff not in results_dict :
            results_dict[literature_eff] = {}

        filename = f"{abbrev_loc}_eff{literature_eff}_Li{literature_Li_conc}.txt"

        initial_data = extract_data(op_location,abbrev_loc,literature_Li_conc, vec_ini)


        prod,m_pumpbr = setup_site(literature_eff,initial_data[abbrev_loc], constants, params = None)

        manager = ProcessManager(initial_data[abbrev_loc],m_pumpbr,prod,process_sequence,filename,constants,params = None)

        result_df = manager.run(filename)

        calculator = ResourceCalculator(result_df)
        results = calculator.calculate_resource_per_prod_mass(production_mass=prod)  # example production mass
        calculator.save_to_csv(results,
                               filename=f'C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\results\\rawdata\\ResourceCalculator\\output_{abbrev_loc}.csv')

        results_dict[literature_eff][literature_Li_conc] = {
            'data_frames' : result_df
            }



        base_directory = f'C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\results\\figures\\results_{abbrev_loc}'

        # Check if the base directory exists, if not create it
        if not os.path.exists(base_directory) :
            os.makedirs(base_directory)

        # Create a new directory for the specific location
        location_directory = os.path.join(base_directory,f'{abbrev_loc}_LCI')
        if not os.path.exists(location_directory) :
            os.makedirs(location_directory)

        # Path for the .pkl file
        file_path = os.path.join(location_directory,
                                 f"results_dict_{abbrev_loc}_{literature_Li_conc}_{literature_eff}.pkl")

        with open(file_path,"wb") as f :
            pickle.dump(results_dict,f)

        print(results_dict)

        print("Simulation completed and results stored in the dictionary.")

        return results_dict,literature_eff,literature_Li_conc



    def run_sensitivity_analysis(self,filename,op_location,abbrev_loc,Li_conc,eff) :

        # Store the original parameters
        original_params = (self.constants.copy())

        results_dict = {}

        for param,values in SENSITIVITY_RANGES.items() :
            # Reset to original parameters before each run
            self.params = original_params.copy()
            for value in values :

                # Ensure no duplicate keys by checking and removing if exists
                if param in self.params :
                    del self.params[param]

                # Update the parameter with the new value
                self.params[param] = value
                result_key = f"{param}|{value}"
                try :
                    # Ensure the initial data and setup are correct for each sensitivity analysis
                    initial_data = extract_data(op_location,abbrev_loc,Li_conc)

                    prod,m_pumpbr = setup_site(eff,initial_data[abbrev_loc],self.constants,self.params)

                    # Initialize ProcessManager for each iteration
                    manager = ProcessManager(initial_data[abbrev_loc],m_pumpbr,prod,self.process_sequence,filename,
                                             self.constants,self.params)

                    df_results = manager.run(filename)
                    calculator = ResourceCalculator(df_results)
                    results = calculator.calculate_resource_per_prod_mass(
                        production_mass=prod)  # example production mass
                    result_key_updated = f"{param}_{value}"
                    calculator.save_to_csv(results, rf'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\ResourceCalculator\Sensitivities\output_{abbrev_loc}_{result_key_updated}.csv')

                    print(result_key)
                    if param not in results_dict :
                        results_dict[param] = {}
                    results_dict[param][value] = {
                        'data_frames' : df_results
                        }
                except Exception as e :
                    print(f"Error running sensitivity analysis for {param}={value}: {e}")

        return results_dict

    def save_results(self, filename):
        with pd.ExcelWriter(f'{filename}.xlsx') as writer:
            for key, df in self.data_frames.items():
                df.to_excel(writer, sheet_name=key)


class ResourceCalculator :
    def __init__(self,data_frames) :
        self.data_frames = data_frames

    def calculate_resource_per_prod_mass(self,production_mass) :
        results = {
            'Heat' : 0,
            'Electricity' : 0,
            'Water' : 0,
            'Chemicals' : {},
            'Waste' : {}
            }

        if production_mass <= 0 :
            return results  # Return early if production_mass is not positive

        energy_sum = elec_sum = water_sum = 0

        for df in self.data_frames.values() :
            energy_sum += df[df['Variables'].str.startswith('E_')]['Values'].sum()
            elec_sum += df[df['Variables'].str.startswith('elec_')]['Values'].sum()
            water_sum += df[df['Variables'].str.startswith('water_')]['Values'].sum()

            # Process each chemical
            for index,row in df[df['Variables'].str.startswith('chemical_')].iterrows() :
                chemical_name = row['Variables'].split('_')[1]
                if chemical_name not in results['Chemicals'] :
                    results['Chemicals'][chemical_name] = 0
                results['Chemicals'][chemical_name] += row['Values']

            # Process each waste
            for index,row in df[df['Variables'].str.startswith('waste_')].iterrows() :
                waste_name = row['Variables'].split('_')[1]
                if waste_name not in results['Waste'] :
                    results['Waste'][waste_name] = 0
                results['Waste'][waste_name] += row['Values']

        # Calculating per production mass
        results['Heat'] = energy_sum / production_mass
        results['Electricity'] = elec_sum / production_mass
        results['Water'] = water_sum / production_mass
        results['Chemicals'] = {k : v / production_mass for k,v in
                                              results['Chemicals'].items()}
        results['Waste'] = {k : v / production_mass for k,v in results['Waste'].items()}

        return results

    def save_to_csv(self,results,filename="output.csv") :
        os.makedirs(os.path.dirname(filename),exist_ok=True)

        # Flatten the dictionary for CSV output
        flattened_data = {
            'Heat' : results['Heat'],
            'Electricity' : results['Electricity'],
            'Water' : results['Water']
            }
        for key,subdict in results.items() :
            if isinstance(subdict,dict) :
                for subkey,value in subdict.items() :
                    flattened_data[f'{key} ({subkey})'] = value

        # Convert to DataFrame and save to CSV
        df = pd.DataFrame([flattened_data])
        df.to_csv(filename,index=False)
        print(f"Data saved to {filename}")

    def compile_resources(directory, file_path) :
        # Extract location_names for abbrev_loc
        excel_data = pd.read_excel(file_path)
        transposed_data = excel_data.transpose()
        transposed_data.columns = transposed_data.iloc[0]
        transposed_data = transposed_data.drop(transposed_data.index[0])

        # Just for ordering in the table

        activity_status_order = {
            # Early stage
            'Grassroots' : '3 - Exploration - Early stage',
            'Exploration' : '3 - Exploration - Early stage',
            'Target Outline' : '3 - Exploration - Early stage',
            'Commissioning' : '3 - Exploration - Early stage',
            'Prefeas/Scoping' : '3 - Exploration - Early stage',
            'Advanced exploration' : '3 - Exploration - Early stage',
            'Feasibility Started' : '3 - Exploration - Early stage',
            # Late stage
            'Reserves Development' : '2 - Exploration - Late stage',
            'Feasibility' : '2 - Exploration - Late stage',
            'Feasibility complete' : '2 - Exploration - Late stage',
            'Construction started' : '2 - Exploration - Late stage',
            'Construction planned' : '2 - Exploration - Late stage',
            # Mine stage
            'Preproduction' : '2 - Exploration - Late stage',
            'Production' : '1 - Mine stage',
            'Operating' : '1 - Mine stage',
            'Satellite' : '1 - Mine stage',
            'Expansion' : '1 - Mine stage',
            'Limited production' : '1 - Mine stage',
            'Residual production' : '1 - Mine stage'
            }

        sites_info = {}

        for site,row in transposed_data.iterrows() :
            activity_status = row.get("activity_status",None)

            production_value = row.get("production",standard_values.get("production"))
            if pd.isna(production_value) :  # Check if the value is nan
                production_value = standard_values.get("production","Unknown")  # Replace with the default if it's nan

            site_info = {
                "site_name" : site,
                "abbreviation" : row["abbreviation"],
                "country_location" : row["country_location"],
                "ini_Li" : row.get("ini_Li",0),
                "ini_Ca": row.get("ini_Ca", 0),
                "ini_Mg": row.get("ini_Mg", 0),
                "ini_SO4": row.get("ini_SO4", 0),
                "ini_B": row.get("ini_B", 0),
                "ini_Si": row.get("ini_Si", 0),
                "ini_Fe": row.get("ini_Fe", 0),
                "ini_Mn": row.get("ini_Mn", 0),
                "ini_Zn": row.get("ini_Zn", 0),
                "Li_efficiency" : row.get("Li_efficiency",None),
                "deposit_type" : row.get("deposit_type",None),
                "technology_group" : row.get("technology_group",None),
                "activity_status" : row.get("activity_status",None),
                "activity_status_order" : activity_status_order.get(activity_status,'4 - Other'),
                "production" : production_value,
                }

            # Using a list comprehension to sum the impurities, handling NaN explicitly
            sum_impurities = sum([0 if np.isnan(site_info.get(key,0)) else site_info.get(key,0)
                                  for key in ["ini_Ca","ini_Mg","ini_SO4","ini_B","ini_Si","ini_Fe","ini_Mn","ini_Zn"]])

            site_info["sum_impurities"] = sum_impurities

            # Add to the main dictionary

            sites_info[site] = site_info

        sites_df = pd.DataFrame.from_dict(sites_info,orient='index').reset_index(drop=True)

        # List all files in the directory
        files = os.listdir(directory)

        # Filter files to only those that match the pattern "output_*.csv"
        filtered_files = [file for file in files if file.startswith('output_') and file.endswith('.csv')]

        # Dictionary to hold data from each site
        all_data = []

        for file in filtered_files :
            # Construct the full file path
            full_path = os.path.join(directory,file)
            # Extract site name from the file name (assumes format "output_{abbrev_loc}.csv")
            abbrev_loc_from_dir = os.path.splitext(file)[0].split('_')[1]
            # Read the CSV file into a DataFrame
            df = pd.read_csv(full_path)

            # Find the matching site name using abbreviation
            match = sites_df.loc[sites_df['abbreviation'] == abbrev_loc_from_dir,'site_name'].values
            site_name = match[0] if match.size > 0 else None

            if site_name is None :
                print(f"No site found for abbreviation: {abbrev_loc_from_dir}")
                continue  # Skip this file if no matching site is found

            # Add columns for site name and 'technology_group'
            df['Site'] = site_name
            #df['Production'] = sites_df.loc[sites_df['site_name'] == site_name,'production'].values[0]
            df['Technology'] = sites_df.loc[sites_df['site_name'] == site_name,'technology_group'].values[0]
            #df['Country'] = sites_df.loc[sites_df['site_name'] == site_name,'country_location'].values[0]
            #df['Activity status'] = sites_df.loc[sites_df['site_name'] == site_name,'activity_status_order'].values[0]
            df['Li wt. %'] = sites_df.loc[sites_df['site_name'] == site_name,'ini_Li'].values[0]
            df['Sum impurities'] = sites_df.loc[sites_df['site_name'] == site_name,'sum_impurities'].values[0]
            df['Energy'] = df['Heat'] * 0.277777778 + df['Electricity'] + (df['Water'] * 2.783 / 1000)

            #print entire df columns
            print(df.columns)


            waste_list = ['Waste (solid)', 'Waste (Na)', 'Waste (Cl)', 'Waste (heat)', 'Waste (organicsolvent)', 'Waste (salt)']

            for waste in waste_list:
                if waste in df.columns:
                    df[waste] = df[waste]
                else:
                    df[waste] = 0

            # if df has column "Waste (solid)" then add salt + solid
            if 'Waste (solid)' in df.columns :
                df['Solid waste'] = df['Waste (solid)'] + df['Waste (salt)']
            else :
                df['Solid waste'] = df['Waste (salt)']

            chemicals_list = ['Chemicals (calciumchloride)', 'Chemicals (organicsolvent)', 'Chemicals (limestone)']

            for chemical in chemicals_list:
                if chemical in df.columns:
                    df[chemical] = df[chemical]
                else:
                    df[chemical] = 0

            df['Chemicals (other)'] = df['Chemicals (calciumchloride)'] + df['Chemicals (organicsolvent)'] + df['Chemicals (limestone)']

            # Set 'location' as the index
            df.set_index('Site',inplace=True)
            df.drop(columns=['Waste (heat)', 'Waste (Na)', 'Waste (Cl)', 'Waste (organicsolvent)',
                             'Waste (salt)', 'Waste (solid)', 'Chemicals (calciumchloride)',
                             'Chemicals (organicsolvent)', 'Chemicals (limestone)'],inplace=True)

            # Reorder columns to make 'technology_group', 'country_location', and 'activity_status' appear first in the DataFrame body
            first_cols = [ 'Technology', 'Li wt. %', 'Sum impurities', 'Energy', 'Heat','Electricity' ]
            other_cols = [col for col in df.columns if col not in first_cols]
            columns_order = first_cols + other_cols
            df = df[columns_order]

            print(f"Adding DataFrame for site: {site_name}")  # Debugging statement
            all_data.append(df)

            if not all_data :
                print("No DataFrames to concatenate.")  # Final check before attempting to concatenate
                return None

        # Combine all DataFrames into one, each as a column
        combined_df = pd.concat(all_data,axis=0)

        # Optional: rearrange multi-level columns if necessary
        combined_df.columns = combined_df.columns.map(lambda x : f'{x[0]}_{x[1]}' if isinstance(x,tuple) else x)

        # Sort the DataFrame by 'technology_group'
        combined_df = combined_df.sort_values(by=['Technology', 'Li wt. %'], ascending=[True, False])

        # Round the numbers in the DataFrame
        # specify the number of decimal places you want to round to
        combined_df = combined_df.round(decimals=4)  # for example, rounding to 2 decimal places

        ResourceCalculator.save_compiled_csv(combined_df,directory, filename = "compiled_resource_data")

        return combined_df

    @staticmethod
    def save_compiled_csv(compiled_data, directory, filename):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(directory, filename + "_" + timestamp + ".csv")
        compiled_data.to_csv(output_path)
        print(f"Data from ResourceCalculator saved to '{output_path}'")


def create_process_instance(process_class, constants, params, custom_name=None):
    try:
        if custom_name is not None:
            return process_class(constants=constants, params=params, custom_name=custom_name)
        else:
            return process_class(constants=constants, params=params)
    except TypeError:
        # If the process class does not accept constants and params
        if custom_name is not None:
            return process_class(custom_name=custom_name)
        else:
            return process_class()




def create_process_instance_old(process_class, constants, params, custom_name=None):
    try:
        if custom_name:
            return process_class(constants=constants, params=params, custom_name=custom_name)
        else:
            return process_class(constants=constants, params=params)
    except TypeError as e:
        print(f"Error: {e}")
        if "missing 1 required positional argument" in str(e) and custom_name:
            return process_class(constants, params, custom_name)
        elif "missing 3 required positional arguments" in str(e):
            return process_class(constants, params, custom_name)
        elif custom_name:
            return process_class(custom_name=custom_name)
        else:
            return process_class()


process_function_map = {
    "evaporation_ponds": lambda constants, params, custom_name=None: create_process_instance(evaporation_ponds, constants, params, custom_name),
    "Centrifuge_general": lambda constants, params, custom_name=None: create_process_instance(Centrifuge_general, constants, params, custom_name),
    "Liprec_TG": lambda constants, params, custom_name=None: create_process_instance(Liprec_TG, constants, params, custom_name),
    "washing_TG": lambda constants, params, custom_name=None: create_process_instance(washing_TG, constants, params, custom_name),
    "CentrifugeTG": lambda constants, params, custom_name=None: create_process_instance(CentrifugeTG, constants, params, custom_name),
    "dissolution": lambda constants, params, custom_name=None: create_process_instance(dissolution, constants, params, custom_name),
    "ion_exchange_H": lambda constants, params, custom_name=None: create_process_instance(ion_exchange_H, constants, params, custom_name),
    "ion_exchange_L": lambda constants, params, custom_name=None: create_process_instance(ion_exchange_L, constants, params, custom_name),
    "Liprec_BG": lambda constants, params, custom_name=None: create_process_instance(Liprec_BG, constants, params, custom_name),
    "CentrifugeBG": lambda constants, params, custom_name=None: create_process_instance(CentrifugeBG, constants, params, custom_name),
    "washing_BG": lambda constants, params, custom_name=None: create_process_instance(washing_BG, constants, params, custom_name),
    "CentrifugeWash": lambda constants, params, custom_name=None: create_process_instance(CentrifugeWash, constants, params, custom_name),
    "rotary_dryer": lambda constants, params, custom_name=None: create_process_instance(rotary_dryer, constants, params, custom_name),
    "DLE_evaporation_ponds": lambda constants, params, custom_name=None: create_process_instance(DLE_evaporation_ponds, constants, params, custom_name),
    "transport_brine": lambda constants, params, custom_name=None: create_process_instance(transport_brine, constants, params, custom_name),
    "B_removal_organicsolvent": lambda constants, params, custom_name=None: create_process_instance(B_removal_organicsolvent, constants, params, custom_name),
    "SiFe_removal_limestone": lambda constants, params, custom_name=None: create_process_instance(SiFeRemovalLimestone, constants, params, custom_name),
    "MnZn_removal_lime": lambda constants, params, custom_name=None: create_process_instance(MnZn_removal_lime, constants, params, custom_name),
    "Li_adsorption": lambda constants, params, custom_name=None: create_process_instance(Li_adsorption, constants, params, custom_name),
    "acidification": lambda constants, params, custom_name=None: create_process_instance(acidification, constants, params, custom_name),
    "CaMg_removal_sodiumhydrox": lambda constants, params, custom_name=None: create_process_instance(CaMg_removal_sodiumhydrox, constants, params, custom_name),
    "CentrifugeSoda": lambda constants, params, custom_name=None: create_process_instance(CentrifugeSoda, constants, params, custom_name),
    "Mg_removal_sodaash": lambda constants, params, custom_name=None: create_process_instance(Mg_removal_sodaash, constants, params, custom_name),
    "Mg_removal_quicklime": lambda constants, params, custom_name=None: create_process_instance(Mg_removal_quicklime, constants, params, custom_name),
    "CentrifugeQuicklime": lambda constants, params, custom_name=None: create_process_instance(CentrifugeQuicklime, constants, params, custom_name),
    "reverse_osmosis": lambda constants, params, custom_name=None: create_process_instance(reverse_osmosis, constants, params, custom_name),
    "triple_evaporator": lambda constants, params, custom_name=None: create_process_instance(triple_evaporator, constants, params, custom_name),
    "sulfate_removal_calciumchloride": lambda constants, params, custom_name=None: create_process_instance(sulfate_removal_calciumchloride, constants, params, custom_name),
    "nanofiltration": lambda constants, params, custom_name=None: create_process_instance(nanofiltration, constants, params, custom_name)
}





process_function_map_2 = {
    "evaporation_ponds": lambda constants, params: evaporation_ponds(constants=constants, params=params),
    "Centrifuge_general": lambda constants, params, custom_name=None: Centrifuge_general(constants=constants, params=params, custom_name=custom_name),
    "Liprec_TG": lambda constants, params: Liprec_TG(constants=constants, params=params),
    "washing_TG": lambda constants, params: washing_TG(constants=constants, params=params),
    "CentrifugeTG": lambda constants, params: CentrifugeTG(constants=constants, params=params),
    "dissolution": lambda constants, params: dissolution(constants=constants, params=params),
    "ion_exchange_H": lambda constants, params, custom_name=None: ion_exchange_H(constants=constants, params=params, custom_name=custom_name),
    "ion_exchange_L": lambda constants, params, custom_name=None: ion_exchange_L(constants=constants, params=params, custom_name=custom_name),
    "Liprec_BG": lambda constants, params: Liprec_BG(constants=constants, params=params),
    "CentrifugeBG": lambda constants, params: CentrifugeBG(constants=constants, params=params),
    "washing_BG": lambda constants, params: washing_BG(constants=constants, params=params),
    "CentrifugeWash": lambda constants, params: CentrifugeWash(constants=constants, params=params),
    "rotary_dryer": lambda constants, params: rotary_dryer(constants=constants, params=params),
    "DLE_evaporation_ponds": lambda constants, params: DLE_evaporation_ponds(constants=constants, params=params),
    "transport_brine": lambda constants, params: transport_brine(constants=constants, params=params),
    "B_removal_organicsolvent": lambda constants, params: B_removal_organicsolvent(constants=constants, params=params),
    "SiFe_removal_limestone": lambda constants, params: SiFeRemovalLimestone(constants=constants, params=params),
    "MnZn_removal_lime": lambda constants, params: MnZn_removal_lime(constants=constants, params=params),
    "Li_adsorption": lambda constants, params: Li_adsorption(constants=constants, params=params),
    "acidification": lambda constants, params: acidification(constants=constants, params=params),
    "CaMg_removal_sodiumhydrox": lambda constants, params: CaMg_removal_sodiumhydrox(constants=constants, params=params),
    "CentrifugeSoda": lambda constants, params: CentrifugeSoda(constants=constants, params=params),
    "Mg_removal_sodaash": lambda constants, params: Mg_removal_sodaash(constants=constants, params=params),
    "Mg_removal_quicklime": lambda constants, params: Mg_removal_quicklime(constants=constants, params=params),
    "CentrifugeQuicklime": lambda constants, params: CentrifugeQuicklime(constants=constants, params=params),
    "reverse_osmosis": lambda constants, params: reverse_osmosis(constants=constants, params=params),
    "triple_evaporator": lambda constants, params: triple_evaporator(constants=constants, params=params),
    "sulfate_removal_calciumchloride": lambda constants, params: sulfate_removal_calciumchloride(constants=constants, params=params),
    "nanofiltration": lambda constants, params: nanofiltration(constants=constants, params=params),
}




process_function_map_old = {
    "evaporation_ponds": evaporation_ponds,
    "Centrifuge_general": Centrifuge_general,
    "Liprec_TG": Liprec_TG,
    "washing_TG": washing_TG,
    "CentrifugeTG": CentrifugeTG,
    "dissolution": dissolution,
    "ion_exchange_H": ion_exchange_H,
    "ion_exchange_L": ion_exchange_L,
    "Liprec_BG": Liprec_BG,
    "CentrifugeBG": CentrifugeBG,
    "washing_BG": washing_BG,
    "CentrifugeWash": CentrifugeWash,
    "rotary_dryer": rotary_dryer,
    "DLE_evaporation_ponds": DLE_evaporation_ponds,
    "transport_brine": transport_brine,
    "B_removal_organicsolvent": B_removal_organicsolvent,
    "SiFe_removal_limestone": SiFeRemovalLimestone,
    "MnZn_removal_lime": MnZn_removal_lime,
    "Li_adsorption": Li_adsorption,
    "acidification": acidification,
    "CaMg_removal_sodiumhydrox": CaMg_removal_sodiumhydrox,
    "CentrifugeSoda": CentrifugeSoda,
    "Mg_removal_sodaash": Mg_removal_sodaash,
    "Mg_removal_quicklime": Mg_removal_quicklime,
    "CentrifugeQuicklime": CentrifugeQuicklime,
    "reverse_osmosis": reverse_osmosis,
    "triple_evaporator": triple_evaporator,
    "sulfate_removal_calciumchloride": sulfate_removal_calciumchloride,
    "nanofiltration": nanofiltration
    }

