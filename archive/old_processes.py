# Centrifuge after TG TODO generalize this function
class centrifuge_TG :
    def execute(self, prod, site_parameters, m_in) :
        Dens_ini = site_parameters['density_brine']  # initial density of brine
        elec_centri = 1.3 * m_in / (Dens_ini * 1000)  # Electricity consumption of centrifuge [kWh]
        waste_centri = -(0.8 * (m_in - 1.5 * prod)) / 1000 #liquid waste in m3 --> reason for /1000
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
