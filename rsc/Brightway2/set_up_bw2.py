import bw2data as bd
import bw2io as bi

def import_biosphere(biosphere_f):
    if biosphere_f in bd.databases:
        print(biosphere_f + " database already present!!! No import is needed")
        pass
    else:
        bi.bw2setup()
        pass



