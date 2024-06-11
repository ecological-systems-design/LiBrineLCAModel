import bw2data as bd
import bw2io as bi
from src.BW2_calculations.setting_up_bio_and_ei import import_biosphere, import_ecoinvent
from src.BW2_calculations.lithium_site_db import *
from src.BW2_calculations.modification_bw2 import *


# create database environment for operational site

def database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location, eff,
                         Li_conc, op_location, abbrev_loc, dataframes_dict, chemical_map):

    #set up general ecoinvent and biosphere databases
    bio = import_biosphere(biosphere)
    ei_reg = import_ecoinvent(ei_path, ei_name)

    #set up site database
    site_db = create_database(site_name, country_location, eff, Li_conc, op_location, abbrev_loc, ei_name, biosphere, dataframes_dict, chemical_map,deposit_type)

    #adapt site database to deposit type
    ei_reg, site_db = adaptions_deposit_type(deposit_type, country_location, op_location, ei_name, site_name)

    ei_reg, site_db = regionalize_activities(ei_name, site_name, op_location, regionalized_activities)

    return ei_reg, site_db, bio










