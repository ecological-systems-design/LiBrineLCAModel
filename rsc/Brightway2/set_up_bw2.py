import bw2data as bd
import bw2io as bi

def import_biosphere(biosphere_f):
    if biosphere_f in bd.databases:
        print(biosphere_f + " database already present!!! No import is needed")
        pass
    else:
        bi.bw2setup()
        pass



# Ecoinvent
def import_ecoinvent(ei_path_f, ei_name_f):
    ei = bi.SingleOutputEcospold2Importer(ei_path_f, ei_name_f)
    ei.apply_strategies()
    ei.match_database(db_name="biosphere3", fields=('name', 'category', 'unit', 'location'))
    ei.statistics()
    ei.write_database()