
import pandas as pd
import bw2calc as bc
import bw2data as bd

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


def print_recursive_calculation(activity, lcia_method, lca_obj=None, file_obj=True, total_score=None, amount=1, level=0,
                                max_level=30, cutoff=0.01) :
    if lca_obj is None :
        lca_obj = bc.LCA({activity : amount}, lcia_method)
        lca_obj.lci()
        lca_obj.lcia()
        total_score = lca_obj.score
    elif total_score is None :
        raise ValueError
    else :
        lca_obj.redo_lcia({activity : amount})
        if abs(lca_obj.score) <= abs(total_score * cutoff) :
            return

    indent = "    " * level
    output = "'{}''{:4.3f}''{:6.10f}': {:.70}\n".format(level, lca_obj.score / total_score, lca_obj.score,
                                                        str(activity))

    if lca_obj.score == 0 :
        print('yea')

    if file_obj :
        file_obj.write(output)
    else :
        print(output)

    if level < max_level :
        for exc in activity.technosphere() :
            print_recursive_calculation(
                activity=exc.input,
                lcia_method=lcia_method,
                lca_obj=lca_obj,
                file_obj=file_obj,
                total_score=total_score,
                amount=amount * exc['amount'],
                level=level + 1,
                max_level=max_level,
                cutoff=cutoff
                )




