from pathlib import Path
import pickle
import os
from rsc.Postprocessing_results.preparing_data import preparing_data_for_LCA_results_comparison, process_data_based_on_excel
from rsc.Postprocessing_results.visualization_functions import *
from rsc.global_analysis.site_LCI_and_LCA import *
from rsc.lithium_production.licarbonate_processes import *
from rsc.Brightway2.lithium_site_db import chemical_map


if not os.path.exists("results") :
    os.mkdir("results")


if __name__ == '__main__' :

    file_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\new_file_lithiumsites.xlsx'
    directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\LCA_results'
    save_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\global_comparison'
    save_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\recursive_calculation'
    site_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\recursive_calculation\results_Chaer\Chaerhan_climatechange_0.022_0.77_20240328_185718_.csv'
    base_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\recursive_calculation'
    #results, sites_info = preparing_data_for_LCA_results_comparison(file_path, directory_path)
    #make the graph
    #Visualization.plot_LCA_results_comparison(file_path, directory_path, save_path)
    #Visualization.plot_LCA_results_comparison_based_on_technology(file_path, directory_path, save_path)

    #Visualization.plot_LCA_results_comparison_based_on_exploration_and_Liconc(file_path,directory_path,save_path)

    #Visualization.plot_LCA_results_bubble_IPCC_AWARE(file_path,directory_path,save_path)

    #Visualization.plot_LCA_results_scatter_Li_conc(file_path,directory_path,save_path)

    #Visualization.plot_LCA_results_comparison_based_on_production_and_Liconc(file_path,directory_path,save_path)
    #run_analysis_for_all_sites(file_path, directory_path)
    #df = prepare_data_for_waterfall_diagram(site_path)


    #Visualization.create_waterfall_plots(site_path, save_dir)

    Visualization.process_data_based_on_excel(file_path,base_dir, save_dir)

    print('Finished the code')




