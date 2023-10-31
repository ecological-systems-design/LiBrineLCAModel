import bw2data as bd
import bw2io as bi
from rsc.Brightway2.setting_up_bio_and_ei import import_biosphere, import_ecoinvent
from rsc.Brightway2.lithium_site_db import create_database, copy_database
from rsc.Brightway2.modification_bw2 import adaptions_deposit_type


# create database environment for operational site

def database_environment(biosphere, ei_path, ei_name, site_name, deposit_type, country_location, eff,
                         Li_conc, op_location, abbrev_loc, dataframes_dict):

    #set up general ecoinvent and biosphere databases
    bio = import_biosphere(biosphere)
    ei_reg = import_ecoinvent(ei_path, ei_name)

    #set up site database
    site_db = create_database(site_name, country_location, eff, Li_conc, op_location, abbrev_loc, ei_name, biosphere, dataframes_dict)

    print(bd.databases)

    #adapt site database to deposit type
    ei_reg, site_db = adaptions_deposit_type(deposit_type, country_location, op_location, ei_name, site_name)

    #site_db_new = copy_database(site_name, f"{site_name}_copy")

    return ei_reg, site_db, bio










