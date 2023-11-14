import bw2data as bd
from pathlib import Path
#from Processes import *
#from chemical_formulas import *
#from operational_data_salton import *
import os
if not os.path.exists("results"):
    os.mkdir("results")



# Databases
ei_path = Path('data/ecoinvent 3.9.1_cutoff_ecoSpold02/datasets')
ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salton_39_test36"
site_path = f'../../Python/Brightway/Geothermal_brines/Salton_Sea_39.xlsx'
water_name = f"Water_39"
water_path = f'../../Python/Brightway/Geothermal_brines/Water_39.xlsx'
biosphere = f"biosphere3"


site_location = site_name[:3]

# Biosphere
if __name__ == '__main__':

    project = f'Site_{site_name}_3'
    bd.projects.set_current(project)

    choice = input("BW2?")

    if choice == "yes":

        choice = input("Do you want to make any changes in databases?: ").lower()

        if choice == "yes":

            from rsc.Brightway2.setting_up_bio_and_ei import import_biosphere

            import_biosphere(biosphere)

            from archive.import_db import ecoinvent, water_database, site_database

            database_list = [ei_name, water_name, site_name]

            for database in database_list :
                if database in bd.databases :
                    choice = input(
                        f"The {database} database already exists. Do you want to delete and re-import it? (yes/no): ").lower()
                    if choice == "yes" :
                        # Delete the existing database
                        del bd.databases[database]
                        print(f"Deleted existing {database} database.")

                        # Import the respective database
                        if database == water_name :
                            water_database(water_path, water_name)
                        elif database == ei_name :
                            ecoinvent(ei_path, ei_name)
                        elif database == site_name :
                            site_database(site_path, site_name)
                        print(f"Imported {database} database.")
                    else:
                        f"{database} will be used with no updates"
                        pass
                else :
                    # Import the database if it doesn't exist
                    if database == water_name :
                        water_database(water_path, water_name)
                    elif database == ei_name :
                        ecoinvent(ei_path, ei_name)
                    elif database == site_name :
                        site_database(site_path, site_name)
                    pass

            #Assigning variables to databases
            bio = bd.Database('biosphere3')
            water = bd.Database(water_name)
            site = bd.Database(site_name)
            ei_reg = bd.Database(ei_name)

            location = 'US-WECC'



            from rsc.Brightway2.modification_bw2 import creating_new_act, creating_supplychain, changing_electricity, changing_heat, \
                changing_water_electricity, wastewater, chinese_coal, create_new_act



            activities_to_copy = [("electricity production, deep geothermal", "US-WECC",
                                   "electricity production, deep geothermal"+ " reg"),
                                  ("market for geothermal power plant, 5.5MWel", "GLO",
                                   "market for geothermal power plant, 5.5MWel" + " reg"),
                                  ("geothermal power plant construction", "RoW",
                                   "geothermal power plant construction" + " reg"),
                                  ("market for deep well, drilled, for geothermal power", "GLO",
                                   "market for deep well, drilled, for geothermal power" + " reg")]

            creating_new_act(activities_to_copy, location)

            activities_to_copy = [('deep well drilling, for deep geothermal power', "WECC",
                                   "deep well drilling, for deep geothermal power"+ " reg")]

            creating_supplychain(activities_to_copy, location)

            activities_to_copy = [('heat production, natural gas, at industrial furnace >100kW', "RoW",
                                   "heat production, natural gas, at industrial furnace >100kW"),
                                  ("market for wastewater, average", "RoW",
                                   "market for wastewater, average" + " reg"),
                                  ("treatment of wastewater, average, wastewater treatment", "RoW",
                                   "treatment of wastewater, average, wastewater treatment" + " reg")]

            creating_new_act(activities_to_copy, site_location)

            act_list = []
            for act in site :
                act_list.append(act)

            changing_electricity(act_list)
            act = [act for act in water if 'Geothermal heat' in act['name'] and location in act['location']][0]
            print(act)
            changing_heat(act)

            act = [act for act in water if 'Water_US' == act['name']][0]
            changing_water_electricity(act)

            act = [act for act in ei_reg if "market for wastewater, average reg" in act['name']][0]
            wastewater(act)

            act = ei_reg.search('hard coal mine operation and hard coal preparation')[2]
            chinese_coal(act)

            country_location = "WECC"
            final_prod = [act for act in site if "df_rotary" in act['name']][0]
            drilling = [act for act in ei_reg if "deep well drilling, for deep geothermal power reg" in act['name']
                        and country_location in act['location']][0]
            location_drill = "WECC"
            create_new_act(final_prod, location_drill)
        elif choice == "no":
            bio = bd.Database('biosphere3')
            water = bd.Database(water_name)
            site = bd.Database(site_name)
            ei_reg = bd.Database(ei_name)

            pass



        #from rsc.Brightway2.AWARE import import_AWARE

        #import_AWARE(ei_reg, bio)

        #from rsc.Brightway2.PM_method import import_PM

        #import_PM(ei_reg, bio)

    else:
        pass


locations = [("Salton Sea", "Sal"), ("Upper Rhine Valley", "URG")]

bio = bd.Database('biosphere3')
water = bd.Database(water_name)
site = bd.Database(site_name)
ei_reg = bd.Database(ei_name)

country_location = "US-WECC"


from rsc.lithium_production.licarbonate_processes import calculate_processingsequence
eff = 0.5
Li_conc = 0.04
abbrev_loc = "Sal"
location = "Salton Sea"
calculate_processingsequence(eff, Li_conc, op_location=location, abbrev_loc=abbrev_loc)

#print all brightway2 databases
print(bd.databases)

#from rsc.lithium_production.creating_inventories import inventories
#demand_all, df = inventories(Li_conc= 0.04, max_eff = 0.9, min_eff = 0.3, eff_steps = 0.1,
#                             max_number_boreholes = 0, borehole_depth = 0)

from rsc.Brightway2.lithium_site_db import create_database

create_database(database_name=site_name, country_location="US", eff=0.5, Li_conc=0.04, op_location="Salton Sea",
                abbrev_loc="Sal", ei_name=ei_name, biosphere=biosphere)

