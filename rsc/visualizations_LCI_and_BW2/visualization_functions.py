import pandas as pd
import plotly.express as px
import os


class Visualization :
    @staticmethod
    def plot_resources_per_kg(results_dict, abbrev_loc) :
        # Ensure the results folder exists
        results_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/images/figures"
        results_folder = os.path.join(results_path, f"results_{abbrev_loc}")
        Visualization.ensure_folder_exists(results_folder)

        # Prepare the data
        data = []
        for efficiency, eff_results in results_dict.items() :
            for Li_conc, results in eff_results.items() :
                energy, elec, water = results['resources_per_kg']
                data.append({'Efficiency' : efficiency, 'Li_conc' : Li_conc, 'Energy' : energy, 'Electricity' : elec,
                             'Water' : water})

        df = pd.DataFrame(data)

        # Plot and save for each resource
        for resource in ['Energy', 'Electricity', 'Water'] :
            fig = px.line(df, x='Li_conc', y=resource, color='Efficiency',
                          title=f'{resource} per kg',
                          labels={'Li_conc' : 'Li Concentration', resource : f'{resource} per kg',
                                  'Efficiency' : 'Efficiency'})
            fig.show()
            # Save the figure
            for efficiency in results_dict.keys() :
                filtered_df = df[df['Efficiency'] == efficiency]
                fig = px.line(filtered_df, x='Li_conc', y=resource,
                              title=f'{resource} per kg',
                              labels={'Li_conc' : 'Li Concentration', resource : f'{resource} per kg'})
                fig.write_html(os.path.join(results_folder, f"{resource}_per_kg_efficiency_{efficiency}.html"))
            fig.write_html(os.path.join(results_folder, f"{resource}_per_kg_all_efficiencies.html"))
            print(fig)

    @staticmethod
    def ensure_folder_exists(folder) :
        if not os.path.exists(folder) :
            os.makedirs(folder)

