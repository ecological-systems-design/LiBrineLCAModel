import bw2data as bd
import bw2io as bi

# Water database

def water_database(water_path, water_name_f):
    if water_name_f in bd.databases:
        print(f"{water_name_f} database already present!!! No import is needed")
    else:
        water = bi.ExcelImporter(water_path)
        water.apply_strategies()
        water.match_database(ei_name)
        water.statistics()
        water.metadata.pop(None)
        list(water.unlinked)
        if len(list(water.unlinked)) == 0:
            water.write_database()


# Salt lake database

def site_database(site_path, site_name):
    if site_name in bd.databases:
        print(f"{site_name} database already present!!! No import is needed")
    else:
        site = bi.ExcelImporter(site_path)
        site.apply_strategies()
        site.match_database(ei_name)
        site.match_database(water_name)
        site.statistics()
        site.metadata.pop(None)
        if len(list(site.unlinked)) == 0:
            site.write_database()
