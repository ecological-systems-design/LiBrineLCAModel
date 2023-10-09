from rsc.lithium_production.creating_inventories import inventories
import pandas as pd
import bw2calc as bc
import bw2io as bi
import bw2data as bd

df = inventories(0.001, 0.9, 0.5, 0.1, 5, 3000)

def create_db(location = "Sal"):
    if location not in bd.databases:
        db = bd.Database(location)
        db.register()
    else:
        pass
    return db

def creating_BW2_processing(inven = df, location = "Sal", country_location = "US-WECC"):
    db = create_db(location)
    name_list = ['df_SiFe_removal_limestone', 'df_MnZn_removal_lime', 'df_acidification', 'df_Li_adsorption',
                 'df_CaMg_removal_sodiumhydrox', 'df_ion_exchange_L', 'df_reverse_osmosis', 'df_triple_evaporator',
                 'df_Liprec_TG', 'df_centrifuge_TG', 'df_washing_TG', 'df_dissolution', 'df_Liprec_BG',
                 'df_centrifuge_BG',
                 'df_washing_BG', 'df_centrifuge_wash', 'df_rotary'
                 ]
    #when "Variables" contain name of name_list, create activity
    for name in name_list:
        if name not in db:
               if name in inven["Variable"]:
                    act = db.new_activity(code = name, name = name, unit = "kg", amount = 1, location = country_location)
                    act.save()
                    #create exchanges based on the "Variable" column in inven
                    for i in range(len(inven["Variable"])):
                        if inven["Variable"][i] == name:
                            exc = act.new_exchange(input = inven["Input"][i], amount = inven["Amount"][i],
                                                   type = inven["Type"][i], unit = inven["Unit"][i])
                            exc.save()
                        else:
                            pass

               else:
                   pass
        else:
            pass





    return db








def initialize_lca(act_new, method):
    lca = bc.LCA({act_new: 1}, method)
    lca.lci()
    lca.lcia()
    return lca.score


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
