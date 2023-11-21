#Chemical and physical properties
#Atomic masses [g/mole]
H = 1.008
Mg = 24.31
B = 10.81
S = 32.07
Ca = 40.08
Li = 6.94
C = 12.011
O = 15.999
Na = 22.99
Cl = 35.45
K = 39.098
Si = 28.085
As = 74.922
Mn = 54.938
Fe = 55.845
Zn = 65.38
Ba = 137.33
Sr = 87.62

gravity_constant = 9.81  #Gravity constant [m/s2]

#Heat capacities of chemicals
#At 100 °C
hCC = 849  #Heat capacity of gaseous CO2
hCH = 1996  #Heat capacity of gaseous H2O

#At 25 °C
hCHH = 4190  #Heat capacity of pure water
hCHH_bri = 3219.94  #Heat capacity - salt concentration 30 %  (30 % NaCl solution) (Ramalingam and  Arumugam, 2012)
hCLi = 1341  #Heat capacity of lithium carbonate

#Heat content
heat_natgas = 40.4  #Heat content of natural gas [MJ/Nm3]
heat_propgas = 44.33  #Heat content of propane gas [MJ/kg]
#Latent heat of water
latheat_H = 2257000  #Latent heat of water [J/kg]

#Densities of required substances/chemicals
dens_NaCl = 2160  #Density of sodium chloride [kg/m3]
dens_Soda = 2540  #Density of soda ash [kg/m3]
dens_CaCl = 2150  #Density of calcium chloride [kg/m3]
dens_Licarb = 2100  #Density of lithium carbonate [kg/m3]
dens_H2O = 1000  #Density of water [kg/m3]
dens_pulp = 2 / 3 * dens_H2O + 1 / 3 * dens_Licarb  #Assumed density of the pulp [kg/m3]
dens_frw= 1100 #Density of fresh water extracted at the Salar de Atacama [kg/m3]
dens_organicsolvent = 818 #Density of organic solvent [kg/m3]

#Dissolution constant of Li2CO3 at 10 °C
dissol_cons = 0.052  #in kg/kg

# Operational temperature ranges
T_Liprec = 83  # Temperature for first Li2CO3 precipitation
T_deion1 = 80  # Temperature for washing water after first Li2CO3 precipitation
T_dissol = 10  # Temperature for dissolution of Li2CO3
T_RO = 40  # Temperature of reverse osmosis
T_evap = 70  # Temperature of triple evaporator
T_desorp = 40  # Temperature in Li-ion adsorption (desorption)
T_adsorp = 85  # Temperature in Li-ion adsorption (adsorption)
T_boron = 10 # Temperature in boron removal
T_Mg_soda = 60 # Temperature in Mg removal by soda ash
T_motherliq = 80 # Temperature of mother liquor

adsorp_capacity = 0.008  # Adsorption capacity of Li-ion adsorption [kg/kg]
adsorb_capacity_salar = 4/(1/1.2)  # Adsorption capacity of Li-ion adsorption [kg/kg]; 1.2 density of resin
Li_out_adsorb = 198 # Li concentration in Li-ion adsorption [mg/L]
Li_out_RO = 5000 # Li concentration in RO permeate [mg/L]
Li_in_RO = 2500 # Li concentration in RO feed [mg/L]
Li_out_evaporator = 30000 # Li concentration in evaporator brine [mg/L]
eff_pw = 0.95 # Efficiency of pumping well

heat_loss = 0.85

# Proxy values
proxy_freshwater_EP = 0.002726891764265545 # mass of pumped fresh water per kg m_saltbri
proxy_harvest = 8.565755621167364e-05

# Boron removal - specific constants
pH_ini = 11  # Initial pH of concentrated brine
pOH_ini = 14 - pH_ini  # Initial pOH of concentrated brine
pH_aft = 1.8  # End pH of concentrated brine by adding HCl solution
pOH_aft = 14 - pH_aft  # End pOH of concentrated brine by adding HCl solution

recycling_rate = 0.985 # Recycling rate of organic solvent
sodiumhydroxide_solution = 0.3 # Assumed 30 wt. % sodium hydroxide solution
sodaash_solution = 0.25 # Assumed 25 wt. % soda ash solution
calciumchloride_solution = 0.3 # Assumed 30 wt. % calcium chloride solution
sulfuricacid_solution = 0.18 # Assumed 18 wt. % sulfuric acid solution (Pastos Grandes project)

Mg_conc_pulp_quicklime = 0.05 # Magnesium concentration in pulp before quicklime addition

quicklime_reaction_factor = 1.2 # Incomplete reaction factor for chemical reactions

evaporator_gor = 16



