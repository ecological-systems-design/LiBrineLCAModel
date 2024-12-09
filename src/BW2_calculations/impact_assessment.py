import pandas as pd
import bw2calc as bc
import bw2data as bd
import os
from src.BW2_calculations.iterating_LCIs import change_exchanges_in_database, change_exchanges_in_database_sensitivity
import datetime
import csv
from src.LifeCycleInventoryModel_Li.operational_and_environmental_constants import SENSITIVITY_RANGES


def calculate_impacts(activity,methods) :
    """
    Calculate impacts of a given activity and amount using specified methods.

    :param activity: A tuple (database, code) identifying the activity.
    :param amount: Amount of the activity.
    :param methods: List of method tuples to be used for LCA calculations.
    :return: Dictionary of impacts for each method.
    """

    impacts = {}

    for method in methods :
        lca = bc.LCA({activity : 1},method=method)
        lca.lci()
        lca.lcia()
        impacts[method] = lca.score
        print(lca.score)

    return impacts


# function to iterate over inventories and calculate impacts
def calculate_impacts_for_selected_scenarios(activity,methods,dict_results,site_name,ei_name,abbrev_loc,eff_range=None,
                                             Li_conc_range=None,literature_eff=None,literature_Li_conc=None,
                                             renewables=None) :
    site_db = bd.Database(site_name)
    ei_reg = bd.Database(ei_name)

    dict_impacts = {}

    # Default to empty lists if ranges are not provided
    if eff_range is None :
        eff_range = []
    if Li_conc_range is None :
        Li_conc_range = []

    # Define the range or single value to use for efficiency and lithium concentration
    eff_to_use = [literature_eff] if literature_eff is not None else eff_range
    Li_conc_to_use = [literature_Li_conc] if literature_Li_conc is not None else Li_conc_range

    # Check if either literature values or ranges are provided
    if len(eff_to_use) == 0 or len(Li_conc_to_use) == 0 :
        raise ValueError(
            "Either literature values or ranges for efficiency and lithium concentration must be provided.")

    # Iterate over the efficiency and lithium concentration values
    for eff in eff_to_use :
        for Li in Li_conc_to_use :
            site_db = change_exchanges_in_database(eff,Li,site_name,abbrev_loc,dict_results)

            # Calculate impacts for the activity
            impacts = calculate_impacts(activity,methods)

            rounded_Li = round(Li,3)
            rounded_eff = round(eff,2)

            if renewables is None :
                file_names = [f"{site_name}_climatechange_{rounded_Li}_{rounded_eff}",
                              f"{site_name}_waterscarcity_{rounded_Li}_{rounded_eff}",
                              f"{site_name}_PM_{rounded_Li}_{rounded_eff}"]
            else :
                file_names = [f"{site_name}_climatechange_{rounded_Li}_{rounded_eff}_renewables",
                              f"{site_name}_waterscarcity_{rounded_Li}_{rounded_eff}_renewables",
                              f"{site_name}_PM_{rounded_Li}_{rounded_eff}_renewables"]

            for method,file_name in zip(methods,file_names) :
                print_recursive_calculation(activity,method,abbrev_loc,file_name,max_level=30,cutoff=0.01)

            # Add impacts to the dictionary and add the efficiency and Li concentration as keys
            dict_impacts[eff,Li] = impacts

    return dict_impacts


def calculate_impacts_for_brine_chemistry(activity,methods,dict_results,site_name,ei_name,abbrev_loc,eff_range=None,
                                          Li_conc_range=None,literature_eff=None,literature_Li_conc=None) :
    site_db = bd.Database(site_name)
    ei_reg = bd.Database(ei_name)

    dict_impacts = {}

    # Default to empty lists if ranges are not provided
    if eff_range is None :
        eff_range = []
    if Li_conc_range is None :
        Li_conc_range = []

    # Define the range or single value to use for efficiency and lithium concentration
    eff_to_use = [literature_eff] if literature_eff is not None else eff_range
    Li_conc_to_use = [literature_Li_conc] if literature_Li_conc is not None else Li_conc_range

    print(f'Lithium concentration to use: {Li_conc_to_use}')

    # Check if either literature values or ranges are provided
    if len(eff_to_use) == 0 or len(Li_conc_to_use) == 0 :
        raise ValueError(
            "Either literature values or ranges for efficiency and lithium concentration must be provided.")

    # Iterate over the efficiency and lithium concentration values
    for eff in eff_to_use :
        for Li in Li_conc_to_use :
            print('abbrev_loc:',abbrev_loc)
            site_db = change_exchanges_in_database(eff,Li,site_name,abbrev_loc,dict_results)

            activity = [act for act in site_db if "df_rotary_dryer" in act['name']][0]


            # Calculate impacts for the activity
            impacts = calculate_impacts(activity,methods)

            rounded_Li = round(Li,3)
            rounded_eff = round(eff,2)

            file_names = [f"{site_name}_climatechange_{rounded_Li}_{rounded_eff}",
                          f"{site_name}_waterscarcity_{rounded_Li}_{rounded_eff}",
                          f"{site_name}_PM_{rounded_Li}_{rounded_eff}"]

            # Add impacts to the dictionary and add the efficiency and Li concentration as keys
            dict_impacts[eff,Li] = impacts

    return dict_impacts


def calculate_impacts_for_sensitivity_analysis(activity,methods,dict_results,site_name,ei_name,abbrev_loc,
                                               threshold=1e-30) :
    site_db = bd.Database(site_name)

    ei_reg = bd.Database(ei_name)

    dict_impacts = {}

    # Calculate impacts for each parameter combination and store them
    for param,values_dict in dict_results.items() :
        #print(param)
        for value in values_dict.keys() :

            # Update the database with the new parameter and value
            site_db = change_exchanges_in_database_sensitivity(param,value,site_name,abbrev_loc,dict_results)


            # Calculate impacts for the activity
            impacts = calculate_impacts(activity,methods)
            result_key = f"{param}|{value}"
            dict_impacts[result_key] = impacts

    # Convert the impacts dictionary to a DataFrame for easy comparison
    results_df = pd.DataFrame(dict_impacts).T

    # Calculate differences between impacts for each method
    for method in methods :
        method_column = results_df[method]
        differences = method_column.diff().abs().dropna()

        # Check for small differences
        small_diffs = differences[differences > threshold]
        if not small_diffs.empty :
            print(f"Small differences detected in method {method} below threshold {threshold}:")
            print(small_diffs)

    print(dict_impacts)
    return dict_impacts





def ensure_folder_exists(folder_path) :
    if not os.path.exists(folder_path) :
        os.makedirs(folder_path)


def saving_LCA_results(results,abbrev_loc,renewable=None) :
    if isinstance(results,dict) :

        # Get efficiency and Li-conc ranges for filename
        efficiencies = [round(eff,2) for (eff,_) in results.keys()]
        Li_concs = [Li_conc for (_,Li_conc) in results.keys()]

        min_eff,max_eff = min(efficiencies),max(efficiencies)
        min_Li_conc,max_Li_conc = min(Li_concs),max(Li_concs)

        filename = f"{abbrev_loc}_eff_{min_eff}_to_{max_eff}_LiConc_{min_Li_conc}_to_{max_Li_conc}"

        # Transforming the dictionary into the desired DataFrame format
        transformed_data = []
        for keys,values in results.items() :
            row = {'Li-conc' : keys[1],'eff' : keys[0]}
            for inner_keys,value in values.items() :
                if inner_keys[0].startswith('IPCC') :
                    row['IPCC'] = value
                elif inner_keys[0].startswith('AWARE') :
                    row['AWARE'] = value
                elif inner_keys[0].startswith('PM') :
                    row['PM'] = value
            transformed_data.append(row)
        results_df = pd.DataFrame(transformed_data)
    else :
        results_df = results

    results_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/results/rawdata"

    if renewable is None :
        # Ensure the results folder exists
        results_folder = os.path.join(results_path,f"LCA_results")
        csv_file_path = os.path.join(results_folder,f"{filename}.csv")
        ensure_folder_exists(results_folder)
    else :
        results_folder = os.path.join(results_path,f"Renewable_assessment")
        csv_file_path = os.path.join(results_folder,f"renewables_{filename}.csv")
        ensure_folder_exists(results_folder)

    # Save the DataFrame as a CSV
    results_df.to_csv(csv_file_path,index=False)  # Add index=False if you don't want to save the index

    print(f"Saved {filename} as CSV file")


def saving_LCA_results_brinechemistry(results,abbrev_loc) :
    if isinstance(results,dict) :

        # Get efficiency and Li-conc ranges for filename
        efficiencies = [round(eff,2) for (eff,_) in results.keys()]
        Li_concs = [Li_conc for (_,Li_conc) in results.keys()]

        min_eff,max_eff = min(efficiencies),max(efficiencies)
        min_Li_conc,max_Li_conc = min(Li_concs),max(Li_concs)

        filename = f"{abbrev_loc}_eff_{min_eff}_to_{max_eff}_LiConc_{min_Li_conc}_to_{max_Li_conc}"

        # Transforming the dictionary into the desired DataFrame format
        transformed_data = []
        for keys,values in results.items() :
            row = {'Li-conc' : keys[1],'eff' : keys[0]}
            for inner_keys,value in values.items() :
                if inner_keys[0].startswith('IPCC') :
                    row['IPCC'] = value
                elif inner_keys[0].startswith('AWARE') :
                    row['AWARE'] = value
                elif inner_keys[0].startswith('PM') :
                    row['PM'] = value
            transformed_data.append(row)
        results_df = pd.DataFrame(transformed_data)
    else :
        results_df = results

    print(results_df)

    # Ensure the results folder exists
    results_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/results/rawdata"
    results_folder = os.path.join(results_path,f"LCA_brinechemistry")
    ensure_folder_exists(results_folder)

    # Save the DataFrame as a CSV
    csv_file_path = os.path.join(results_folder,f"{filename}.csv")
    results_df.to_csv(csv_file_path,index=False)  # Add index=False if you don't want to save the index

    print(f"Saved {filename} as CSV file")


def saving_sensitivity_results(results,abbrev_loc,save_dir, renewable=None) :
    if not isinstance(results,dict) :
        print("Results are not in dictionary format.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{abbrev_loc}_sensitivity_analysis_{timestamp}.xlsx"

    # Define impact types
    ipcc_impact = ('IPCC 2021','climate change','global warming potential (GWP100)')
    aware_impact = ('AWARE regionalized','Annual','All')

    # Transforming the dictionary into two lists for each impact type
    ipcc_data = []
    aware_data = []

    for param,values_dict in results.items() :
        for impact_tuple,impact_value in values_dict.items() :
            row = {'param' : param,'value' : impact_value}
            if impact_tuple == ipcc_impact :
                ipcc_data.append(row)
            elif impact_tuple == aware_impact :
                aware_data.append(row)

    # Create DataFrames
    ipcc_df = pd.DataFrame(ipcc_data)
    aware_df = pd.DataFrame(aware_data)

    #use save_dir to save the file in the desired directory
    filename = os.path.join(save_dir,filename)

    # Save to Excel with separate sheets
    with pd.ExcelWriter(filename) as writer :
        ipcc_df.to_excel(writer,sheet_name='IPCC',index=False)
        aware_df.to_excel(writer,sheet_name='AWARE',index=False)

    print(f"Data successfully saved to {filename}")


def saving_sensitivity_results_old(results, abbrev_loc, renewable=None):
    if isinstance(results, dict):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{abbrev_loc}_sensitivity_analysis_{timestamp}"

        # Transforming the dictionary into the desired DataFrame format
        transformed_data = []
        for param, values_dict in results.items():
            for value_tuple, impact_dict in values_dict.items():
                value = value_tuple if isinstance(value_tuple, (int, float)) else value_tuple[0]
                row = {'param': param, 'value': float(value)}
                for impact_category, impact_data in impact_dict['data_frames'].items():
                    if impact_category.startswith('IPCC'):
                        row['IPCC'] = impact_data
                    elif impact_category.startswith('AWARE'):
                        row['AWARE'] = impact_data
                    elif impact_category.startswith('PM'):
                        row['PM'] = impact_data
                transformed_data.append(row)
        results_df = pd.DataFrame(transformed_data)
    else:
        print("Results are not in dictionary format.")
        return







def print_recursive_calculation(activity,lcia_method,abbrev_loc,filename,lca_obj=None,results_df=None,
                                total_score=None,amount=1,level=0,max_level=30,cutoff=0.01) :
    base_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/results/recursive_calculation"
    if activity['name'] == "df_rotary_dryer" :
        results_folder = os.path.join(base_path,f"results_{abbrev_loc}")
    else :
        results_folder = os.path.join(base_path,f"battery")
        filename = filename + f'_{abbrev_loc}'

    ensure_folder_exists(results_folder)

    # Initialize DataFrame at the top level
    if level == 0 :
        results_df = pd.DataFrame(columns=['Level','Fraction','Score','Activity'])

    # LCA calculation logic
    if lca_obj is None :
        lca_obj = bc.LCA({activity : amount},lcia_method)
        lca_obj.lci()
        lca_obj.lcia()
        total_score = lca_obj.score
    elif total_score is None :
        raise ValueError("Total score is None.")
    else :
        lca_obj.redo_lcia({activity : amount})
        if abs(lca_obj.score) <= abs(total_score * cutoff) :
            return results_df

    # Append data to DataFrame
    fraction = lca_obj.score / total_score if total_score else 0
    results_df = results_df.append(
        {'Level' : level,'Fraction' : fraction,'Score' : lca_obj.score,'Activity' : str(activity)},
        ignore_index=True)

    # print(f"Level {level}: Appended data. DataFrame now has {len(results_df)} rows.")  # Debugging print

    # Recursive call for each technosphere exchange
    if level < max_level :
        for exc in activity.technosphere() :
            results_df = print_recursive_calculation(
                activity=exc.input,
                lcia_method=lcia_method,
                abbrev_loc=abbrev_loc,
                filename=filename,
                lca_obj=lca_obj,
                results_df=results_df,
                total_score=total_score,
                amount=amount * exc['amount'],
                level=level + 1,
                max_level=max_level,
                cutoff=cutoff
                )

    # Save results to CSV at the top level
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = filename + f'_{timestamp}_' + ".csv"
    if level == 0 :
        file_path = os.path.join(results_folder,filename)
        results_df.to_csv(file_path,index=False)
        print(f"Results saved in {file_path}")

    # Return the DataFrame
    return results_df


def calculate_battery_impacts(battery_act,methods,site_db,ei_reg,country) :
    lithium_act = [act for act in site_db if "df_rotary_dryer" in act['name']][0]
    market_lithium_act = [act for act in ei_reg if "market for lithium carbonate" in act['name']][0]

    exc = [exc for exc in market_lithium_act.exchanges()]

    for exc in exc :
        exc.delete()

    market_lithium_act.new_exchange(input=lithium_act.key,amount=1,type='technosphere',unit='kilogram',formula=1,
                                    location=country).save()
    market_lithium_act.save()

    dict_impacts = {}

    for method in methods :
        lca = bc.LCA({battery_act : 1},method=method)
        lca.lci()
        lca.lcia()
        dict_impacts[method] = lca.score

    return dict_impacts


def save_battery_results_to_csv(directory, results, abbrev_loc, battery_act, energy_type):
    # Mapping of battery names to filenames
    battery_files = {
        "NMC811": f"NMC811_results_{energy_type}.csv",
        "LFP": f"LFP_results_{energy_type}.csv"
    }

    # Extract battery type from the activity name
    battery_type = None
    for key in battery_files.keys():
        if key in battery_act['name']:
            battery_type = key
            break

    # Check if the battery type was found and get the filename
    if battery_type:
        filename = os.path.join(directory, battery_files[battery_type])
    else:
        print('Battery type not recognized')
        return  # Exit the function early if battery type is not recognized

    # Check if the directory exists; if not, create it
    os.makedirs(directory, exist_ok=True)

    # Prepare to write results to CSV
    headers = ['Method', 'Site', 'Impact Score']
    new_file = not os.path.exists(filename)

    method_dict = {
        "('IPCC 2021', 'climate change', 'global warming potential (GWP100)')": 'IPCC 2021',
        "('AWARE regionalized', 'Annual', 'All')": "AWARE"
    }

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if new_file:
            writer.writerow(headers)  # Write headers if it's a new file
        for method, score in results.items():
            # Check if method is in method_dict and use the corresponding value if it is
            method_name = method_dict.get(method, method)
            writer.writerow([method_name, abbrev_loc, score])
