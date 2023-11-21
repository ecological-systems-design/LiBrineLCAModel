
import pandas as pd
import bw2calc as bc
import bw2data as bd
import os
from rsc.Brightway2.iterating_LCIs import change_exchanges_in_database


def calculate_impacts(activity, methods) :
    """
    Calculate impacts of a given activity and amount using specified methods.

    :param activity: A tuple (database, code) identifying the activity.
    :param amount: Amount of the activity.
    :param methods: List of method tuples to be used for LCA calculations.
    :return: Dictionary of impacts for each method.
    """

    impacts = {}

    for method in methods :
        lca = bc.LCA({activity : 1}, method=method)
        lca.lci()
        lca.lcia()
        impacts[method] = lca.score
        print(lca.score)

    return impacts


#function to iterate over inventories and calculate impacts
def calculate_impacts_for_selected_scenarios(activity, methods, dict_results, site_name, ei_name, eff_range,
                                             Li_conc_range, abbrev_loc) :
    site_db = bd.Database(site_name)
    ei_reg = bd.Database(ei_name)

    dict_impacts = {}

    #Change exchanges in site_db by using the function change_exchanges_in_database
    for eff in eff_range:
        for Li in Li_conc_range:
            site_db = change_exchanges_in_database(eff, Li, site_name, abbrev_loc, dict_results)

            # Calculate impacts for the activity
            impacts = calculate_impacts(activity, methods)

            # Add impacts to the dictionary and add the efficiency and Li concentration as keys
            dict_impacts[eff, Li] = impacts

    return dict_impacts

def ensure_folder_exists(folder_path) :
    if not os.path.exists(folder_path) :
        os.makedirs(folder_path)

def saving_LCA_results(results, filename, abbrev_loc):

    if isinstance(results, dict) :
        # Transforming the dictionary into the desired DataFrame format
        transformed_data = []
        for keys, values in results.items() :
            row = {'Li-conc' : keys[0], 'eff' : keys[1]}
            for inner_keys, value in values.items() :
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
    results_folder = os.path.join(results_path, f"LCA_results_{abbrev_loc}")
    ensure_folder_exists(results_folder)

    # Save the DataFrame as a CSV
    csv_file_path = os.path.join(results_folder, f"{filename}.csv")
    results_df.to_csv(csv_file_path, index=False) # Add index=False if you don't want to save the index

    print(f"Saved {filename} as CSV file")

def print_recursive_calculation(activity, lcia_method, abbrev_loc, filename, lca_obj=None, results_df=None, total_score=None, amount=1, level=0, max_level=30, cutoff=0.01):
    base_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/results/recursive_calculation"
    results_folder = os.path.join(base_path, f"results_{abbrev_loc}")
    ensure_folder_exists(results_folder)

    # Initialize DataFrame at the top level
    if level == 0:
        results_df = pd.DataFrame(columns=['Level', 'Fraction', 'Score', 'Description'])

    # LCA calculation logic
    if lca_obj is None:
        lca_obj = bc.LCA({activity: amount}, lcia_method)
        lca_obj.lci()
        lca_obj.lcia()
        total_score = lca_obj.score
    elif total_score is None:
        raise ValueError("Total score is None.")
    else:
        lca_obj.redo_lcia({activity: amount})
        if abs(lca_obj.score) <= abs(total_score * cutoff):
            return results_df

    # Append data to DataFrame
    fraction = lca_obj.score / total_score if total_score else 0
    results_df = results_df.append(
        {'Level': level, 'Fraction': fraction, 'Score': lca_obj.score, 'Description': str(activity)},
        ignore_index=True)

    #print(f"Level {level}: Appended data. DataFrame now has {len(results_df)} rows.")  # Debugging print

    # Recursive call for each technosphere exchange
    if level < max_level:
        for exc in activity.technosphere():
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
    if level == 0:
        file_path = os.path.join(results_folder, filename)
        results_df.to_csv(file_path, index=False)
        print(f"Results saved in {file_path}")

    # Return the DataFrame
    return results_df

