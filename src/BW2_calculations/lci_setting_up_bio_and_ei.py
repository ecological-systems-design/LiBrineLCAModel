import bw2data as bd
import bw2io as bi


def import_biosphere(biosphere_f):
    if biosphere_f in bd.databases:
        print(biosphere_f + " database already present!!! No import is needed")
        bio = bd.Database(biosphere_f)
        bio_list = [flow for flow in bio]
        if bio_list == []:
            bi.bw2setup()
        pass
    else:
        bi.bw2setup()
        pass

    bio = bd.Database(biosphere_f)
    return bio




# Ecoinvent
def import_ecoinvent(ei_path_f, ei_name_f):
    if ei_name_f not in bd.databases:
        ei = bi.SingleOutputEcospold2Importer(ei_path_f, ei_name_f)
        ei.apply_strategies()
        ei.match_database(db_name="biosphere3", fields=('name', 'category', 'unit', 'location'))
        ei.statistics()
        ei.write_database()
    else:
        print(ei_name_f + " database already present!!! No import is needed")
        ei_reg = bd.Database(ei_name_f)
        ei_list = [flow for flow in ei_reg]
        if ei_list == []:
            ei = bi.SingleOutputEcospold2Importer(ei_path_f, ei_name_f)
            ei.apply_strategies()
            ei.match_database(db_name="biosphere3", fields=('name', 'category', 'unit', 'location'))
            ei.statistics()
            ei.write_database()
        pass

    ei_reg = bd.Database(ei_name_f)
    return ei_reg