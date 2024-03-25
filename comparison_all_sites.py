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
    directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\LCA_results'
    save_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\global_comparison'
    #results, sites_info = preparing_data_for_LCA_results_comparison(file_path, directory_path)
    #make the graph
    #Visualization.plot_LCA_results_comparison(file_path, directory_path, save_path)
    Visualization.plot_LCA_results_comparison_based_on_technology(file_path, directory_path, save_path)

    Visualization.plot_LCA_results_comparison_based_on_exploration_and_Liconc(file_path,directory_path,save_path)

    Visualization.plot_LCA_results_comparison_based_on_production_and_Liconc(file_path,directory_path,save_path)
    #run_analysis_for_all_sites(file_path, directory_path)

    #TODO: check Chaerhan with dilution factor from previous paper

