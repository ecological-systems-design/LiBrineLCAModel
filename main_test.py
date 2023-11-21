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