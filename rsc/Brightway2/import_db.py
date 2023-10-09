import bw2data as bd
import bw2io as bi


ei_name = f"ecoinvent 3.9.1 cutoff"
site_name = f"Salton_39"
water_name = f"Water_39"
biosphere = f"biosphere3"


# Ecoinvent
def ecoinvent(ei_path_f, ei_name_f):
    ei = bi.SingleOutputEcospold2Importer(ei_path_f, ei_name_f)
    ei.apply_strategies()
    ei.match_database(db_name="biosphere3", fields=('name', 'category', 'unit', 'location'))
    ei.statistics()
    ei.write_database()


def water_database(water_path, water_name_f):
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
    site = bi.ExcelImporter(site_path)
    site.apply_strategies()
    site.match_database(ei_name)
    site.match_database(water_name)
    site.statistics()
    site.metadata.pop(None)
    if len(list(site.unlinked)) == 0:
        site.write_database()
