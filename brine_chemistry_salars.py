from pathlib import Path
import pickle
import os
from src.Postprocessing_results.preparing_data import preparing_data_for_LCA_results_comparison
from src.Postprocessing_results.visualization import *
from src.Model_Setup_Options.calculation_setup import *
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *

if not os.path.exists("results") :
    os.mkdir("results")


if __name__ == '__main__' :

    file_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\new_file_lithiumsites.xlsx'
    directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\LCA_brinechemistry'
    save_directory = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\LCA_brinechemistry'
    result_directory = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\LCA_brinechemistry'


    #generate_dataframes_for_brinechemistry(file_path, save_directory)
    #process_generated_dataframes(file_path, save_directory, result_directory)


    run_analysis_for_brinechemistry(file_path, directory_path)

    Visualization.create_plots_from_brinechemistry(directory_path, save_directory)
