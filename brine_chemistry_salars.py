from pathlib import Path
import pickle
import os
from rsc.Postprocessing_results.preparing_data import preparing_data_for_LCA_results_comparison
from rsc.Postprocessing_results.visualization_functions import *
from rsc.global_analysis.site_LCI_and_LCA import *
from rsc.lithium_production.licarbonate_processes import *

if not os.path.exists("results") :
    os.mkdir("results")


if __name__ == '__main__' :

    file_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\new_file_lithiumsites.xlsx'
    directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\LCA_brinechemistry'
    save_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\LCA_brinechemistry'

    run_analysis_for_brinechemistry(file_path, directory_path)

    Visualization.create_plots_from_brinechemistry(directory_path, save_path)
