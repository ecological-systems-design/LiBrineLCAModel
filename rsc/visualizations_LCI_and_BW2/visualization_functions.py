import pandas as pd
import plotly.express as px
import os
import numpy as np
import plotly.io as pio


class Visualization :
    @staticmethod
    def format_impact_category_name(impact_category) :
        main_category, _, _ = impact_category
        return main_category.replace(" ", "_").replace("(", "").replace(")", "")

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


    def plot_impact_categories(results_dict, abbrev_loc) :
        # Ensure the results folder exists
        results_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/images/figures"
        results_folder = os.path.join(results_path, f"results_{abbrev_loc}")
        Visualization.ensure_folder_exists(results_folder)

        # First, identify all the unique impact categories
        impact_categories = set()
        for impacts in results_dict.values() :
            impact_categories.update(impacts.keys())

        # Define a nice color sequence
        color_sequence = px.colors.qualitative.Antique

        # Define a professional font
        font_family = "Arial"

        # Get efficiency and Li-conc ranges for filename
        efficiencies = [round(eff, 1) for (eff, _) in results_dict.keys()]
        Li_concs = [Li_conc for (_, Li_conc) in results_dict.keys()]

        min_eff, max_eff = min(efficiencies), max(efficiencies)
        min_Li_conc, max_Li_conc = min(Li_concs), max(Li_concs)

        filename_suffix = f"eff_{min_eff}_to_{max_eff}_LiConc_{min_Li_conc}_to_{max_Li_conc}"

        # Then, for each impact category, gather data and plot
        for impact_category in impact_categories :
            formatted_impact_category = Visualization.format_impact_category_name(impact_category)

            data = []
            for (efficiency, Li_conc), impacts in results_dict.items() :
                impact_value = impacts.get(impact_category,
                                           0)  # Provide a default value of 0 if impact_category is not present
                data.append({'Li_conc': Li_conc, 'Efficiency': round(efficiency, 1), 'Impact': impact_value})

            df = pd.DataFrame(data)

            # Plot for all efficiencies
            fig_all_efficiencies = px.line(df, x='Li_conc', y='Impact', color='Efficiency',
                                           title=f'{formatted_impact_category}',
                                           labels={'Li_conc' : 'Li Concentration',
                                                   'Impact' : f'{formatted_impact_category}'},
                                           color_discrete_sequence=color_sequence)

            # Update the layout for a more professional look
            fig_all_efficiencies.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family=font_family, size=12, color='black'),
                title_font=dict(family=font_family, size=16, color='black'),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey', zeroline=False, showline=True,
                           showticklabels=True, linecolor='black', linewidth=2, ticks='outside', tickwidth=2, ticklen=5,
                           tickfont=dict(family=font_family, size=12, color='black')),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey', zeroline=False, showline=True,
                           showticklabels=True, linecolor='black', linewidth=2, ticks='outside', tickwidth=2, ticklen=5,
                           tickfont=dict(family=font_family, size=12, color='black')),
                legend=dict(title='Adsorption yield', x=0.80, y=0.99, bgcolor='rgba(255, 255, 255, 1)', bordercolor='black',
                            borderwidth=1),
                autosize=True,
                margin=dict(autoexpand=True, l=100, r=20, t=110, b=70),
                showlegend=True,
                xaxis_range=[0, df['Li_conc'].max()],
                yaxis_range=[0, df['Impact'].max()]
                )

            # Save the plot as PNG
            png_file_path = os.path.join(results_folder,
                                         f"{abbrev_loc}_{formatted_impact_category}_{filename_suffix}.png")
            fig_all_efficiencies.write_image(png_file_path, width=800, height=600)

            # Save the plot as HTML
            html_file_path = os.path.join(results_folder,
                                          f"{abbrev_loc}_{formatted_impact_category}_{filename_suffix}.html")
            fig_all_efficiencies.write_html(html_file_path)

            print(f"Saved {formatted_impact_category} (All Efficiencies) plot as PNG and HTML.")






