from src.Postprocessing_results.preparing_data import preparing_data_for_LCA_results_comparison, process_data_based_on_excel, process_battery_scores, prepare_table_for_energy_provision_comparison
from src.Postprocessing_results.visualization import *
from src.Model_Setup_Options.calculation_setup import *
from src.LifeCycleInventoryModel_Li.licarbonate_processes import *
if not os.path.exists("results") :
    os.mkdir("results")


if __name__ == '__main__' :

    file_path = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\data\new_file_lithiumsites.xlsx'
    directory_path = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\rawdata\LCA_results'
    sensitivity_directory_path = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\rawdata\sensitivity_results'
    renewable_directory_path = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\rawdata'
    renewable_energy_directory_path = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\rawdata\Renewable_assessment'
    save_path = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\figures\global_comparison'
    save_dir = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\figures\recursive_calculation'
    renewable_save_dir = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\figures\Renewables'
    base_dir = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\recursive_calculation'
    resources_dir = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\rawdata\ResourceCalculator'
    battery_dir = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\recursive_calculation\battery'

    NMC_nonrenew_dir = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\rawdata\battery_assessment\NMC811_results_non_renewable.csv'
    LFP_nonrenew_dir = r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\rawdata\battery_assessment\LFP_results_non_renewable.csv'

    #Run the code
    run_analysis_for_all_sites(file_path, directory_path)

    run_local_sensitivity_analysis_for_all_sites(file_path, sensitivity_directory_path)

    run_analysis_for_all_sites_to_extract_dbs(file_path, directory_path)

    ResourceCalculator.compile_resources(resources_dir, file_path)
    Visualization.process_data_based_on_excel(file_path, base_dir, save_dir)

    Visualization.plot_LCA_results_comparison_based_on_technology(file_path, directory_path, save_path)

    Visualization.plot_LCA_results_comparison_based_on_exploration_and_Liconc(file_path,directory_path,save_path)

    Visualization.plot_LCA_results_bubble_IPCC_AWARE(file_path,directory_path,save_path)

    Visualization.plot_LCA_results_scatter_Li_conc(file_path,directory_path,save_path)
    Visualization.plot_LCA_results_comparison_based_on_production_and_impurities(file_path,directory_path,save_path)

    Visualization.plot_LCA_results_comparison_based_on_production_and_Liconc(file_path,directory_path,save_path)
    Visualization.create_absolute_horizontal_bars(file_path, base_dir, save_dir)

    process_battery_scores(NMC_nonrenew_dir,file_path,
                           r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\figures\LCA_battery')

    process_battery_scores(LFP_nonrenew_dir,file_path,
                            r'C:\Users\Schenker\PycharmProjects\LiBrineLCAModel\results\figures\LCA_battery')
