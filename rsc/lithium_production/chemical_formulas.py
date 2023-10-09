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

#Dissolution constant of Li2CO3 at 10 °C
dissol_cons = 0.052  #in kg/kg

# Operational temperature ranges
T_Liprec = 83  # Temperature for first Li2CO3 precipitation
T_deion1 = 80  # Temperature for washing water after first Li2CO3 precipitation
T_dissol = 10  # Temperature for dissolution of Li2CO3
T_RO = 40  # Temperature of reverse osmosis
T_evap = 70  # Temperature of triple evaporator
T_desorp = 40  # Temperature in Li-ion adsorption (desorption)


heat_loss = 0.85
