#Solid liquid separation by centrifuge 1
elec_centri1=1.3*m_bri_proc_out/(Dens_ini*1000) #electricity consumption of centrifuge [kWh]
waste_centri1=0
centri_out1=m_bri_proc_out #no information on how much solids are separated in this

parameter_list=[centri_out1, m_bri_proc_out, elec_centri1, waste_centri1]

#Solid liquid separation by centrifuge 2
centri_out2=m_bri_soda-MgCO3_waste-NaCl_waste #mass [kg] going out of centrifuge 2
waste_centri2= MgCO3_waste+NaCl_waste #solid residual as waste [kg]
elec_centri2=waste_centri2/100

parameter_list=[centri_out2, m_bri_soda, elec_centri2, waste_centri2]

#Solid liquid separation by centrifuge 3
centri_out3=m_bri_Mg-waste_CaMg #mass [kg] going out of centrifuge 3
waste_centri3=waste_CaMg #waste (residual solids) production [kg]
elec_centri3=waste_centri3/100 #electricity consumption of centrifuge [kWh]

parameter_list=[centri_out3, m_bri_Mg, elec_centri3, waste_centri3]


#Solid liquid separation by centrifuge 4
centri_out4=1.5*prod #mass going out of centrifuge 4 [kg]
waste_centri4=prod_NaCl2 #waste (residual solids) production [kg]
elec_centri4=waste_centri4/100

parameter_list=[centri_out4, mass_Liprec, elec_centri4, waste_centri4]

#Solid liquid separation by centrifuge 5
centri_out5=1.5*prod #mass going out of centrifuge 5 [kg]
waste_centri5=water_deion2_h2o-centri_out5 #waste (residual solids) production [kg]
elec_centri5=centri_out5/100

parameter_list=[centri_out5, water_deion2_h2o, elec_centri5, waste_centri5]

#Solid liquid separation by centrifuge 6
centri_out6=1.7*prod #mass going out of centrifuge 6 [kg]
waste_centri6=wash_out-centri_out6 #waste (residual solids) production [kg]
elec_centri6=centri_out6/100
parameter_list=[centri_out6, wash_out, elec_centri6, waste_centri6]

#Solid liquid separation by centrifuge 1
elec_centri1=1.3*m_bri_proc/(Dens_ini*1000) #electricity consumption of centrifuge [kWh]
centri_out1=m_bri_proc # solids are removed, no assumption how much this is
waste_centri1=0

#Solid liquid separation by centrifuge 2
centri_out2=10*prod #mass going out of centrifuge 2 [kg]
waste_centri2= Liprec1_out-centri_out2 #waste_centri2 is sent back to evaporation ponds [kg]
elec_centri2=centri_out2/100

#Solid liquid separation by centrifuge 3
centri_out3=dissol_out ##waste (residual solids) production [kg], solids are neglected
waste_centri3=0
elec_centri3=1.3*(dissol_out/1100)

#Solid liquid separation by centrifuge 4
centri_out4=prod ##waste (residual solids) production [kg], solids are neglected
waste_centri4=0
elec_centri4=centri_out4/100

#Solid liquid separation by centrifuge 1
centri_out1=m_bri_soda-MgCO3_waste-NaCl_waste #mass [kg] going out of centrifuge 1
waste_centri1= MgCO3_waste+NaCl_waste #solid residual as waste [kg]
elec_centri1=waste_centri1/100

#Solid liquid separation by centrifuge 2
centri_out2=m_bri_Mg-waste_CaMg #mass [kg] going out of centrifuge 2
waste_centri2= waste_CaMg #waste (residual solids) production [kg]
elec_centri2=waste_centri2/100

#Solid liquid separation by centrifuge 3
centri_out3=1.5*prod #mass going out of centrifuge 3 [kg]
waste_centri3=prod_NaCl2 #waste (residual solids) production [kg]
elec_centri3=centri_out3/100

#Solid liquid separation by centrifuge 4, Mother liquor sent back to Mg removal
centri_out4=1.5*prod #mass going out of centrifuge 4 [kg]
elec_centri4=centri_out4/100

#Solid liquid separation by centrifuge 5
centri_out5=1.5*prod #mass going out of centrifuge 5 [kg]
waste_centri5= wash_out-centri_out5  #waste (residual liquid) production [kg]
elec_centri5=centri_out5/100

import pandas as pd


class CentrifugeBase :
    def __init__(self, process_name, density_key, prod_factor, waste_liquid_factor=None, waste_solid_factor=None,
                 recycle_factor=None) :
        self.process_name = process_name
        self.density_key = density_key
        self.prod_factor = prod_factor
        self.waste_liquid_factor = waste_liquid_factor
        self.waste_solid_factor = waste_solid_factor
        self.recycle_factor = recycle_factor

    def execute(self, prod, site_parameters, m_in) :
        # Get the initial density from the site parameters
        Dens_ini = site_parameters[self.density_key]

        # Calculate electricity consumption of the centrifuge
        elec_centri = 1.3 * m_in / (Dens_ini * 1000)

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
            'Ca_mass_brine': None
            }


# To create specific centrifuge processes, we now extend the base class without redefining execute unless necessary.
class CentrifugeTG(CentrifugeBase) :
    def __init__(self) :
        super().__init__(
            process_name='df_centrifuge_TG',
            density_key='density_brine',
            prod_factor=1.5,
            waste_liquid_factor=-0.8 / 1000,
            recycle_factor=0.2
            )


class CentrifugeBG(CentrifugeBase) :
    def __init__(self) :
        super().__init__(
            process_name='df_centrifuge_BG',
            density_key='density_brine',
            prod_factor=1.5,
            waste_liquid_factor=-1 / 1000
            )


class CentrifugeWash(CentrifugeBase) :
    def __init__(self) :
        super().__init__(
            process_name='df_centrifuge_wash',
            density_key='density_brine',
            prod_factor=1.5,
            waste_liquid_factor=-1 / 1000
            )


# Example usage:
site_parameters = {'density_brine' : 1200}  # Example site parameters
prod = 100  # Example product mass
m_in = 200  # Example input mass

centrifuge_tg = CentrifugeTG()
centrifuge_bg = CentrifugeBG()
centrifuge_wash = CentrifugeWash()

tg_output = centrifuge_tg.execute(prod, site_parameters, m_in)
bg_output = centrifuge_bg.execute(prod, site_parameters, m_in)
wash_output = centrifuge_wash.execute(prod, site_parameters, m_in)

# Now you can use tg_output, bg_output, wash_output for further processing
