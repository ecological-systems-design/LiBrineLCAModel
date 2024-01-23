from rsc.global_analysis.site_LCI_and_LCA import run_operation_analysis_with_literature_data
from rsc.lithium_production.licarbonate_processes import *

if __name__ == '__main__' :
    project = "Lithium production"
    site_name = "Sal de Vida"
    site_location = "Sal de Vida"
    country_location = "AR"
    process_sequence = [
        evaporation_ponds(),
        Mg_removal_sodaash(),
        CentrifugeSoda(),
        ion_exchange_H(custom_name = None),
        Liprec_TG(),
        washing_TG(),
        CentrifugeTG(),
        dissolution(),
        Liprec_BG(),
        CentrifugeBG(),
        washing_BG(),
        CentrifugeWash(),
        rotary_dryer()
        ]
    impacts = run_operation_analysis_with_literature_data(project, site_name, site_location, country_location, process_sequence)