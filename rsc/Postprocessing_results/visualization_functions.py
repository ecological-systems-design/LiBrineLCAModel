import pandas as pd
import plotly.express as px
import os
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime


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
        results_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/results/figures"
        results_folder = os.path.join(results_path, f"results_{abbrev_loc}")
        Visualization.ensure_folder_exists(results_folder)
        # Define a nice color sequence
        color_sequence = px.colors.qualitative.Antique

        # Define a professional font
        font_family = "Arial"

        resources = ['Energy', 'Electricity', 'Water']
        for resource in resources :
            data = []
            for efficiency, Li_conc_results in results_dict.items() :
                for Li_conc, results in Li_conc_results.items() :
                    resource_value = results['resources_per_kg'][resources.index(resource)]
                    data.append({'Li_conc' : Li_conc, 'Efficiency' : round(efficiency, 1), resource : resource_value})

            df = pd.DataFrame(data)

            # Customize the plot appearance
            fig_all_efficiencies = px.line(
                df, x='Li_conc', y=resource, color='Efficiency',
                title=f'{resource} per kg Li2CO3',
                labels={'Li_conc' : 'Li Concentration', resource : f'{resource} (per kg)'},
                markers=True, color_discrete_sequence=color_sequence
                )

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
                legend=dict(title='Efficiency', x=1.05, y=1, bgcolor='rgba(255, 255, 255, 1)',
                            bordercolor='black',
                            borderwidth=1, orientation="v"),
                autosize=True,
                margin=dict(autoexpand=True, l=100, r=20, t=110, b=70),
                showlegend=True,
                xaxis_range=[0, df['Li_conc'].max()],
                yaxis_range=[0, df[resource].max()]
                )

            # Save the plot as PNG
            png_file_path = os.path.join(results_folder, f"{abbrev_loc}_{resource.lower()}_per_kg_all_efficiencies.png")
            fig_all_efficiencies.write_image(png_file_path, width=800, height=600)

            # Save the plot as HTML
            html_file_path = os.path.join(results_folder,
                                          f"{abbrev_loc}_{resource.lower()}_per_kg_all_efficiencies.html")
            fig_all_efficiencies.write_html(html_file_path)

            print(f"Saved {resource} per kg plot as PNG and HTML.")


    def plot_impact_categories(results_dict, abbrev_loc) :
        # Ensure the results folder exists
        results_path = "C:/Users/Schenker/PycharmProjects/Geothermal_brines/results/figures"
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
                                           markers=True,
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
                legend=dict(title='Efficiency', x=1.05, y=1, bgcolor='rgba(255, 255, 255, 1)',
                            bordercolor='black',
                            borderwidth=1, orientation="v"),
                autosize=True,
                margin=dict(autoexpand=True, l=100, r=20, t=110, b=70),
                showlegend=True,
                xaxis_range=[0, df['Li_conc'].max()],
                yaxis_range=[0, df['Impact'].max()]
                )

            # Generate a timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save the plot as PNG
            png_file_path = os.path.join(results_folder,
                                         f"{abbrev_loc}_{formatted_impact_category}_{filename_suffix}_{timestamp}.png")
            fig_all_efficiencies.write_image(png_file_path, width=800, height=600)

            # Save the plot as HTML
            html_file_path = os.path.join(results_folder,
                                          f"{abbrev_loc}_{formatted_impact_category}_{filename_suffix}_{timestamp}.html")
            fig_all_efficiencies.write_html(html_file_path)

            print(f"Saved {formatted_impact_category} plot as PNG and HTML.")

    def plot_lca_results_comparison(directory_path) :
        """
        Plots LCA results from CSV files in the given directory with subplots for each category and specific styling.

        :param directory_path: Path to the directory containing CSV files.
        """
        # List all CSV files in the directory
        csv_files = [file for file in os.listdir(directory_path) if file.endswith('.csv')]

        # Define the categories to plot and color sequence
        categories = ['IPCC', 'PM', 'AWARE']
        color_sequence = px.colors.qualitative.Antique

        # Initialize subplots
        fig = make_subplots(rows=len(categories), cols=1, subplot_titles=categories)

        # Data container for all files
        all_data = []

        # Process each CSV file
        for file in csv_files :
            file_path = os.path.join(directory_path, file)
            data = pd.read_csv(file_path)
            site_name = file.split('_')[0]
            data['Site'] = site_name
            all_data.append(data)

        # Combine all data into a single DataFrame
        combined_data = pd.concat(all_data)

        # Create and display bar charts for each category
        for i, category in enumerate(categories, start=1) :
            for site in combined_data['Site'].unique() :
                site_data = combined_data[combined_data['Site'] == site]
                fig.add_trace(
                    go.Bar(x=[site], y=site_data[category], name=site,
                           marker_color=color_sequence[i % len(color_sequence)]),
                    row=i, col=1
                    )

        # Update the layout for a more professional look
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12, color='black'),
            title_font=dict(family="Arial", size=16, color='black'),
            showlegend=True,
            legend=dict(title='Site', x=1.05, y=1, bgcolor='rgba(255, 255, 255, 1)', bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True, l=100, r=20, t=110, b=70)
            )

        # Adjust axis settings for each subplot
        for i in range(len(categories)) :
            fig.update_xaxes(row=i + 1, col=1, showgrid=True, gridwidth=1, gridcolor='lightgrey', zeroline=False,
                             showline=True,
                             showticklabels=True, linecolor='black', linewidth=2, ticks='outside', tickwidth=2,
                             ticklen=5,
                             tickfont=dict(family="Arial", size=12, color='black'))
            fig.update_yaxes(row=i + 1, col=1, range=[0, combined_data[category].max()], showgrid=True, gridwidth=1, gridcolor='lightgrey', zeroline=False,
                             showline=True,
                             showticklabels=True, linecolor='black', linewidth=2, ticks='outside', tickwidth=2,
                             ticklen=5,
                             tickfont=dict(family="Arial", size=12, color='black'))

        # Directory for LCA comparison results
        lca_comparison_dir = os.path.join(directory_path, 'LCA_allsites')

        Visualization.ensure_folder_exists(lca_comparison_dir)

        # Generate a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save the plot as PNG and HTML
        file_suffix = f"LCA_allsites_{timestamp}.png"
        png_file_path = os.path.join(directory_path, file_suffix)
        fig.write_image(png_file_path, width=800, height=600 * len(categories))

        file_suffix = f"LCA_allsites_{timestamp}.html"
        html_file_path = os.path.join(directory_path, file_suffix)
        fig.write_html(html_file_path)

        print(f"Saved LCA Results plot as PNG and HTML in {directory_path}.")

    def create_sankey_diagram(data, directory_path, abbrev_loc, efficiency_level, li_conc_level) :
        """
        Creates a Sankey diagram based on the specified efficiency and Li-concentration levels.

        :param data: The complex nested dictionary containing the process data.
        :param efficiency_level: The efficiency level to extract data from.
        :param li_conc_level: The Li-concentration level to extract data from.
        """
        # Extract the relevant data
        selected_data = data[efficiency_level][li_conc_level]['data_frames']

        # Extracting process step names and m_output values
        process_steps = list(selected_data.keys())
        m_outputs = [selected_data[step]['Values'][0] for step in process_steps]  # Assuming first value is m_output

        # Preparing data for Sankey diagram
        labels = process_steps
        source = [i for i in range(len(process_steps) - 1)]
        target = [i + 1 for i in range(len(process_steps) - 1)]
        values = m_outputs[:-1]

        # Create the Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels
                ),
            link=dict(
                source=source,
                target=target,
                value=values
                ))])


        fig.update_layout(title_text="Sankey Diagram for Lithium Carbonate Production Process", font_size=10)

        # Directory for LCA comparison results
        lci_comparison_dir = os.path.join(directory_path, f'LCI_sankey_{abbrev_loc}')

        Visualization.ensure_folder_exists(lci_comparison_dir)

        # Generate a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save the plot as PNG and HTML
        file_suffix = f"LCI_{abbrev_loc}_{timestamp}.png"
        png_file_path = os.path.join(lci_comparison_dir, file_suffix)
        fig.write_image(png_file_path, width=800, height=600)

        file_suffix = f"LCI_{abbrev_loc}_{timestamp}.html"
        html_file_path = os.path.join(lci_comparison_dir, file_suffix)
        fig.write_html(html_file_path)








