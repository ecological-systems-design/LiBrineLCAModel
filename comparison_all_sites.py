from pathlib import Path
import pickle
import os
from src.Postprocessing_results.preparing_data import preparing_data_for_LCA_results_comparison, process_data_based_on_excel, process_battery_scores, prepare_table_for_energy_provision_comparison
from src.Postprocessing_results.visualization_functions import *
from src.Model_Setup_Options.site_LCI_and_LCA import *
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
import bw2data as bd
if not os.path.exists("results") :
    os.mkdir("results")


if __name__ == '__main__' :

    file_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\new_file_lithiumsites.xlsx'
    directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\LCA_results'
    sensitivity_directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\sensitivity_results'
    renewable_directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata'
    renewable_energy_directory_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\Renewable_assessment'
    save_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\global_comparison'
    save_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\recursive_calculation'
    renewable_save_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\Renewables'
    base_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\recursive_calculation'
    resources_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\ResourceCalculator'
    battery_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\recursive_calculation\battery'

    NMC_nonrenew_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\battery_assessment\NMC811_results_non_renewable.csv'
    LFP_nonrenew_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata\battery_assessment\LFP_results_non_renewable.csv'


    #run_analysis_for_all_sites(file_path, directory_path)
    run_local_sensitivity_analysis_for_all_sites(file_path, directory_path)
    # # #
    # prepare_table_for_energy_provision_comparison(file_path, renewable_directory_path, renewable_save_dir)
    # # #
    # run_analysis_for_all_sites_to_extract_dbs(file_path, directory_path)
    # # #
    # ResourceCalculator.compile_resources(resources_dir, file_path)
    # # #
    # Visualization.process_data_based_on_excel(file_path, base_dir, save_dir)
    # # # #
    # # # #Visualization.plot_all_sites(file_path, base_dir, save_dir)
    # #Visualization.plot_LCA_results_comparison(file_path, directory_path, save_path)
    # Visualization.plot_LCA_results_comparison_based_on_technology(file_path, directory_path, save_path)
    # # # # #
    # Visualization.plot_LCA_results_comparison_based_on_exploration_and_Liconc(file_path,directory_path,save_path)
    # # # # #
    # Visualization.plot_LCA_results_bubble_IPCC_AWARE(file_path,directory_path,save_path)
    # # # # # #
    # Visualization.plot_LCA_results_scatter_Li_conc(file_path,directory_path,save_path)
    # # # # # #
    Visualization.plot_LCA_results_comparison_based_on_production_and_impurities(file_path,directory_path,save_path)
    #
    # Visualization.plot_LCA_results_comparison_based_on_production_and_Liconc(file_path,renewable_energy_directory_path,save_path)
    # # # # # #
    # Visualization.create_relative_horizontal_bars(file_path, base_dir, save_dir)

    #process_battery_scores(NMC_nonrenew_dir,file_path,
    #                       r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\LCA_battery')

    #process_battery_scores(LFP_nonrenew_dir,file_path,
    #                        r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\LCA_battery')



    # #Go into file path and extract all the site_names from the excel file
    # # get location-specific data by importing xlsx file
    # excel_data = pd.read_excel(file_path)
    # # Transpose the data for easier processing
    # transposed_data = excel_data.transpose()
    # # Set the first row as the header
    # transposed_data.columns = transposed_data.iloc[0]
    # # Drop the first row since it's now the header
    # transposed_data = transposed_data.drop(transposed_data.index[0])
    # sites_info = {}
    #
    # for site,row in transposed_data.iterrows() :
    #
    #     site_info = {
    #         "site_name" : site,
    #         }
    #
    #     sites_info[site] = site_info
    #
    # # Convert 'sites_info' to DataFrame for easier manipulation
    # sites_df = pd.DataFrame.from_dict(sites_info,orient='index').reset_index(drop=True)
    # print(sites_df)
    #
    # #Create a list with the site_name and "Site_{site_name}_number"; numbers should go from 1 to 25
    # for site_name in sites_df['site_name']:
    #
    #     project = "default"
    #     #Create a list with the site_name and "Site_{site_name}_number"; numbers should go from 1 to 25
    #     for i in range(1,3):
    #         project_old = f'Site_{site_name}_literature_values_test{i}'
    #         if project_old in bd.projects:
    #             print(f'Project {project_old} exists')
    #             bd.projects.delete_project(project_old,delete_dir=True)
    #             bd.projects.set_current(project)
    #         else:
    #             print(f'Project {project_old} does not exist')
    #
    #
    #
    #
    #
