import pandas as pd
import plotly.express as px
import os
import numpy as np
import plotly.io as pio


class Visualization :
    @staticmethod
    def ensure_folder_exists(folder_path) :
        if not os.path.exists(folder_path) :
            os.makedirs(folder_path)

    @staticmethod
    def plot_resources_per_kg(results_dict, abbrev_loc) :
        # Ensure the results folder exists
        results_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/images/figures"
        results_folder = os.path.join(results_path, f"results_{abbrev_loc}")
        Visualization.ensure_folder_exists(results_folder)

        resources = ['Energy', 'Electricity', 'Water']
        for resource in resources :
            data = []
            for efficiency, Li_conc_results in results_dict.items() :
                for Li_conc, results in Li_conc_results.items() :
                    resource_value = results['resources_per_kg'][resources.index(resource)]
                    data.append({'Li_conc' : Li_conc, 'Efficiency' : efficiency, resource : resource_value})

            df = pd.DataFrame(data)

            # Plot for all efficiencies
            fig_all_efficiencies = px.line(df, x='Li_conc', y=resource, color='Efficiency',
                                           title=f'{resource} per kg (All Efficiencies)',
                                           labels={'Li_conc' : 'Li Concentration', resource : f'{resource} per kg'})

            # Save the plot as PNG
            png_file_path = os.path.join(results_folder, f"{abbrev_loc}_{resource}_per_kg_all_efficiencies.png")
            fig_all_efficiencies.write_image(png_file_path, width=800, height=600)

            # Save the plot as HTML
            html_file_path = os.path.join(results_folder, f"{abbrev_loc}_{resource}_per_kg_all_efficiencies.html")
            fig_all_efficiencies.write_html(html_file_path)

            print(f"Saved {resource} per kg (All Efficiencies) plot as PNG and HTML.")

