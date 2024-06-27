# Global model to estimate life cycle impacts of lithium mining from brines

## Description

This repository contains the global model to estimate life cycle impacts of lithium mining from brines. The model is implemented in Python and uses the Brightway2 framework for life cycle assessment. The model is based on the following publication:
XXX

## Assessment of lithium mining from brines - single site

Directories in the code need to be changed to own settings.

1. Import of relevant input data from excel file stored in \data (e.g., location, brine chemistry, etc.) -> import_site_parameters.py
2. Modeling of lithium extraction from brines based on processing_sequence -> licarbonate_processes.py
3. Import of biosphere and ecoinvent -> setting_up_bio_and_ei.py
4. Creating site-specific database -> lithium_site_db.py
5. Modification of specific activities for further regionalization -> modification_bw2.py
6. Import impact categories (AWARE, PM) and link with existing databases -> lci_method_aware.py, lci_method_pm.py
7. Calculation of life cycle impacts -> impact_assessment.py
8. Contributional analysis of functional unit -> contributional_analysis_processes.py
9. Visualization of results -> visualization.py

Assessment of all sites in this publication can be performed using the comparison_all_sites.py
