def calculate_processingsequence(eff, Li_conc, location, abbrev_loc, required_data):

    # Initialize lists to store the sums
    process_name = []
    df_list = []

    prod, m_pumpbr = setup_site(site_parameters= required_data[abbrev_loc])
    m_out, df_SiFe_removal_limestone = proc_SiFe_removal_limestone(site_parameters= required_data[abbrev_loc], m_in=m_pumpbr)
    m_out, df_MnZn_removal_lime, Ca_mass_brine = proc_MnZn_removal_lime(site_parameters= required_data[abbrev_loc], m_in=df_SiFe_removal_limestone.iloc[0, 1])
    m_out, df_acidification = proc_acidification(site_parameters= required_data[abbrev_loc], m_in=df_MnZn_removal_lime.iloc[0, 1])
    m_out, df_adsorption = proc_Li_adsorption(prod, site_parameters= required_data[abbrev_loc], m_in=df_acidification.iloc[0, 1])
    m_out, df_CaMg_removal_sodiumhydrox = proc_CaMg_removal_sodiumhydrox(site_parameters= required_data[abbrev_loc], Ca_mass_leftover=Ca_mass_brine,
                                                                         m_in=df_adsorption.iloc[0, 1])
    m_out, df_ion_exchange_L = proc_ion_exchange_L(site_parameters= required_data[abbrev_loc], m_in=df_CaMg_removal_sodiumhydrox.iloc[0, 1])
    m_out, df_reverse_osmosis, water_RO = proc_reverse_osmosis(site_parameters= required_data[abbrev_loc], m_in=df_ion_exchange_L.iloc[0, 1])
    m_out, df_triple_evaporator, water_evap = proc_triple_evaporator(site_parameters= required_data[abbrev_loc], m_in=df_reverse_osmosis.iloc[0, 1])
    m_out, df_Liprec_TG = proc_Liprec_TG(prod, site_parameters= required_data[abbrev_loc], m_in=df_triple_evaporator.iloc[0, 1])
    m_out, df_washing_TG = proc_washing_TG(prod, site_parameters= required_data[abbrev_loc], m_in=df_Liprec_TG.iloc[0, 1])
    m_out, df_centrifuge_TG = proc_centrifuge_TG(prod, site_parameters= required_data[abbrev_loc], m_in=df_washing_TG.iloc[0, 1])
    m_out, df_dissolution, mass_CO2, prod_libicarb = proc_dissolution(prod, site_parameters= required_data[abbrev_loc], m_in=df_centrifuge_TG.iloc[0, 1])
    m_out, df_Liprec_BG = proc_Liprec_BG(mass_CO2, prod_libicarb, prod, site_parameters= required_data[abbrev_loc], m_in=df_dissolution.iloc[0, 1])
    m_out, df_centrifuge_BG = proc_centrifuge_BG(prod, site_parameters= required_data[abbrev_loc], m_in=df_Liprec_BG.iloc[0, 1])
    m_out, df_washing_BG = proc_washing_BG(prod, site_parameters= required_data[abbrev_loc], m_in=df_centrifuge_BG.iloc[0, 1])
    m_out, df_centrifuge_wash = proc_centrifuge_wash(prod, site_parameters= required_data[abbrev_loc], m_in=df_washing_BG.iloc[0, 1])
    m_out, df_rotary = proc_rot_dry(prod, site_parameters= required_data[abbrev_loc], m_in=df_centrifuge_wash.iloc[0, 1])

    #adaptions for df_adsorption
    update_df_adsorption(df_adsorption, water_RO, water_evap, df_reverse_osmosis, df_triple_evaporator, T_desorp, hCHH,
                         heat_loss, site_parameters= required_data[abbrev_loc])

    df_list = [
        df_SiFe_removal_limestone, df_MnZn_removal_lime, df_acidification, df_adsorption,
        df_CaMg_removal_sodiumhydrox, df_ion_exchange_L, df_reverse_osmosis, df_triple_evaporator,
        df_Liprec_TG, df_centrifuge_TG, df_washing_TG, df_dissolution, df_Liprec_BG, df_centrifuge_BG,
        df_washing_BG, df_centrifuge_wash, df_rotary
        ]

    print(df_list)

    water_sums = []
    elec_sums = []
    E_sums = []

    # Iterate through each step and calculate the sums
    for process_df in df_list :
        water_sums.append(process_df[process_df['Variables'].str.contains('water_')]['Values'].sum())
        elec_sums.append(process_df[process_df['Variables'].str.contains('elec')]['Values'].sum())
        E_sums.append(process_df[process_df['Variables'].str.contains('E_')]['Values'].sum())



    # Create a DataFrame to display the sums for each step
    summary_df = pd.DataFrame({
        'Water Sum' : water_sums,
        'Elec Sum' : elec_sums,
        'E_ Sum' : E_sums,
        'Production': prod
        })

    print(summary_df)

    # Calculate the sums for each column
    water_sum_total = sum(water_sums) / prod
    elec_sum_total = sum(elec_sums) / prod
    E_sum_total = sum(E_sums) / prod

    summary_tot_df = pd.DataFrame({
        'Water_sum per output' : [water_sum_total],
        'Electricity_sum per output' : [elec_sum_total],
        'Energy_sum per output' : [E_sum_total]
        })

    return df_list, summary_df, summary_tot_df

