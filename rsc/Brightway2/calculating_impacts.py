from rsc.lithium_production.creating_inventories import inventories
import pandas as pd
import bw2calc as bc
import bw2io as bi
import bw2data as bd


def calculate_impacts(activity, amount, methods) :
    """
    Calculate impacts of a given activity and amount using specified methods.

    :param activity: A tuple (database, code) identifying the activity.
    :param amount: Amount of the activity.
    :param methods: List of method tuples to be used for LCA calculations.
    :return: Dictionary of impacts for each method.
    """

    impacts = {}

    for method in methods :
        lca = bc.LCA({activity : amount}, method=method)
        lca.lci()
        lca.lcia()
        impacts[method] = lca.score

    return impacts


def calculate_impacts_for_selected_methods(activities, amounts) :
    """
    Calculate LCA impacts for given activities using selected methods and return a dataframe.

    :param activities: List of activity tuples.
    :param amounts: List of amounts for the activities.
    :return: Pandas DataFrame with LCA results.
    """

    # Filter methods based on your criteria
    method_cc = [m for m in bd.methods if 'IPCC 2021' in str(m) and 'climate change' in str(m)
                 and 'global warming potential' in str(m)][-20]

    method_water = [m for m in bd.methods if "AWARE" in str(m)][0]

    method_PM = [m for m in bd.methods if "PM regionalized" in str(m)][0]

    # Consolidate all methods
    methods = method_cc + [method_water, method_PM]

    # Gather results for all activities
    data = []
    for activity, amount in zip(activities, amounts) :
        impacts = calculate_impacts(activity, amount, methods)
        data.append(impacts)

    # Convert to dataframe
    df = pd.DataFrame(data, index=activities)

    return df

def calculating_impacts(Li_conc, drilling_per_year, method, method_PM, method_water):

    name_list = ['df_SiFe_removal_limestone', 'df_MnZn_removal_lime', 'df_acidification', 'df_Li_adsorption',
                 'df_CaMg_removal_sodiumhydrox', 'df_ion_exchange_L', 'df_reverse_osmosis', 'df_triple_evaporator',
                 'df_Liprec_TG', 'df_centrifuge_TG', 'df_washing_TG', 'df_dissolution', 'df_Liprec_BG',
                 'df_centrifuge_BG',
                 'df_washing_BG', 'df_centrifuge_wash', 'df_rotary'
                 ]

    demand_all, df_in = inventories(Li_conc,  )
    iterator = list(range(int(len(df_in) / 17)))
    myarr = [0 for a in range(len(demand_all['Li']))]

    store_LCA = pd.DataFrame({ 'kg CO2 eq' : myarr})

    l = 0

    for j in range(len(iterator)) :
        df_exc = df_in[j * 17 :(j + 1) * 17]

        for i in range(len(name_list)) :

            act = [act for act in site if name_list[i] == act['name']][0]

            k = 0

            for exc in act.exchanges() :
                t = exc['amount']
                exc['amount'] = df_exc[i].iloc[k, 2]
                exc.save()
                # if t == df_exc[i].iloc[k,2]:
                # print('yes')
                # else:
                # print('no')
                # pass
                k += 1
            act.save()

        print(f'{j + 1}. LCI updated')

        print('LCA with updated LCI')
        # fu = [act for act in salar if "df_rotary" in act['name']]
        # assert len(fu)==1
        # fu = fu[0]

        drilling_depth = drilling_per_year[l]
        print("Drilling meter: " + str(drilling_depth))
        act_new = [act for act in water if "Geothermal Li" in act['name']][0]
        exc = [exc for exc in act_new.exchanges()][1]
        production = production_tot[l]
        store_LCA.loc[l, 'drilling tot'] = drilling_depth * production_tot[l]
        exc['amount'] = drilling_depth / production
        store_LCA.loc[l, "drilling"] = exc['amount']
        print(exc['amount'])
        exc.save()

        store_LCA.loc[l, 'kg CO2 eq'] = initialize_lca(method)
        store_LCA.loc[l, "pm impacts"] = initialize_lca(method_PM)
        store_LCA.loc[l, "water scarcity"] = initialize_lca(method_water)

        store_LCA = pd.concat([demand_all, store_LCA], axis = 1)

        l += 1
    return store_LCA
