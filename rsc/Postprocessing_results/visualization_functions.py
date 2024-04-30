import pandas as pd
import plotly.express as px
import os
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from rsc.Postprocessing_results.preparing_data import preparing_data_for_LCA_results_comparison, prepare_data_for_waterfall_diagram, find_latest_matching_file


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

        resources = [ 'Energy', 'Electricity', 'Water' ]
        for resource in resources :
            data = [ ]
            for efficiency, Li_conc_results in results_dict.items() :
                for Li_conc, results in Li_conc_results.items() :
                    resource_value = results[ 'resources_per_kg' ][ resources.index(resource) ]
                    data.append({'Li_conc' : Li_conc, 'Efficiency' : round(efficiency, 2), resource : resource_value})

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
                xaxis_range=[ 0, df[ 'Li_conc' ].max() ],
                yaxis_range=[ 0, df[ resource ].max() ]
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
        efficiencies = [ round(eff, 1) for (eff, _) in results_dict.keys() ]
        Li_concs = [ Li_conc for (_, Li_conc) in results_dict.keys() ]

        min_eff, max_eff = min(efficiencies), max(efficiencies)
        min_Li_conc, max_Li_conc = min(Li_concs), max(Li_concs)

        filename_suffix = f"eff_{min_eff}_to_{max_eff}_LiConc_{min_Li_conc}_to_{max_Li_conc}"

        # Then, for each impact category, gather data and plot
        for impact_category in impact_categories :
            formatted_impact_category = Visualization.format_impact_category_name(impact_category)

            data = [ ]
            for (efficiency, Li_conc), impacts in results_dict.items() :
                impact_value = impacts.get(impact_category,
                                           0)  # Provide a default value of 0 if impact_category is not present
                data.append({'Li_conc' : Li_conc, 'Efficiency' : round(efficiency, 1), 'Impact' : impact_value})

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
                xaxis_range=[ 0, df[ 'Li_conc' ].max() ],
                yaxis_range=[ 0, df[ 'Impact' ].max() ]
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


    def create_sankey_diagram(data, directory_path, abbrev_loc, efficiency_level, li_conc_level) :
        """
        Creates a Sankey diagram based on the specified efficiency and Li-concentration levels.

        :param data: The complex nested dictionary containing the process data.
        :param efficiency_level: The efficiency level to extract data from.
        :param li_conc_level: The Li-concentration level to extract data from.
        """
        # Extract the relevant data
        selected_data = data[ efficiency_level ][ li_conc_level ][ 'data_frames' ]

        # Extracting process step names and m_output values
        process_steps = list(selected_data.keys())
        m_outputs = [ selected_data[ step ][ 'Values' ][ 0 ] for step in
                      process_steps ]  # Assuming first value is m_output

        # Preparing data for Sankey diagram
        labels = process_steps
        source = [ i for i in range(len(process_steps) - 1) ]
        target = [ i + 1 for i in range(len(process_steps) - 1) ]
        values = m_outputs[ :-1 ]

        # Create the Sankey diagram
        fig = go.Figure(data=[ go.Sankey(
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
                )) ])

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

    def plot_LCA_results_comparison(file_path, directory_path, save_dir) :
        matched_results, sites_info = preparing_data_for_LCA_results_comparison(file_path, directory_path)

        # Modify the site name to include Li concentration in the desired format with three decimal places
        for site in sites_info :
            li_conc = float(sites_info[ site ][ 'ini_Li' ])
            sites_info[ site ][ 'ini_Li' ] = f"{site} ({li_conc:.3f} wt. %)"

        # Sort the sites first by country, then by Li concentration within each country
        combined_data = {sites_info[ site ][ 'ini_Li' ] : {'IPCC' : matched_results[ site ][ 'IPCC' ],
                                                           'AWARE' : matched_results[ site ][ 'AWARE' ],
                                                           'country' : sites_info[ site ][ 'country_location' ]}
                         for site in matched_results}

        sorted_data = sorted(combined_data.items(), key=lambda x : (x[ 1 ][ 'country' ],
                                                                    -float(x[ 0 ].split('(')[ 1 ].split(' wt.')[
                                                                               0 ].strip())))

        # Extracting sorted data for the plot
        sorted_sites = [ site for site, _ in sorted_data ]
        ipcc_values = [ data[ 'IPCC' ] for _, data in sorted_data ]
        aware_values = [ data[ 'AWARE' ] for _, data in sorted_data ]

        # Creating subplots
        fig = make_subplots(rows=2, cols=1)

        # Adding IPCC subplot with no x-axis names and dark red color
        fig.add_trace(
            go.Bar(x=sorted_sites, y=ipcc_values, name='Climate change impacts', marker_color='rgb(139, 0, 0)'),
            row=1, col=1
            )
        # Remove x-axis labels for the first plot
        fig.update_xaxes(tickvals=[ ], row=1, col=1)

        # Adding AWARE subplot with blue color
        fig.add_trace(
            go.Bar(x=sorted_sites, y=aware_values, name='Water scarcity impacts', marker_color='rgb(0, 0, 139)'),
            row=2, col=1
            )

        # Customizing the layout to accommodate the larger plot and other requirements
        font_family = "Arial"
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=font_family, size=14, color='black'),
            title='LCA Results per Site (Grouped by Country)',
            showlegend=False,
            legend=dict(title='Impact Type', x=1.05, y=1, bgcolor='rgba(255, 255, 255, 1)', bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True, l=100, r=20, t=110, b=70),
            autosize=False,
            width=1200,  # Adjust the width to your preference
            height=600,  # Adjust the height to your preference
            )

        # Update axes properties to add grids, lines, and ticks
        axis_settings = dict(
            showgrid=True, gridwidth=1, gridcolor='lightgrey', zeroline=False, showline=True,
            linecolor='black', linewidth=2, ticks='outside', tickwidth=2, ticklen=5,
            tickfont=dict(family=font_family, size=12, color='black')
            )

        fig.update_xaxes(axis_settings)
        fig.update_yaxes(axis_settings, title_text="kg CO2eq/ kg Li2CO3", row=1, col=1)
        fig.update_yaxes(axis_settings, title_text="m3 world eq/kg Li2CO3", row=2, col=1)

        # Add text labels for impact types
        fig.add_annotation(text="Climate change impacts", xref="paper", yref="paper", x=1, y=0.95, showarrow=False)
        fig.add_annotation(text="Water scarcity impacts", xref="paper", yref="paper", x=1, y=0.45, showarrow=False)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check if save directory exists, if not, create it
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        # Save the figure to the specified directory
        save_path_png = os.path.join(save_dir, f'LCA_Comparison_Plot_{timestamp}.png')
        fig.write_image(save_path_png)

        save_path_svg = os.path.join(save_dir, f'LCA_Comparison_Plot_{timestamp}.svg')
        fig.write_image(save_path_svg)

        save_path_html = os.path.join(save_dir, f'LCA_Comparison_Plot_{timestamp}.html')
        fig.write_html(save_path_html)

        print(f"Figure saved to {save_path_png} and {save_path_html}")

    def plot_LCA_results_comparison_based_on_technology(file_path, directory_path, save_dir) :
        matched_results, sites_info = preparing_data_for_LCA_results_comparison(file_path, directory_path)

        # Modify the site name to include Li concentration in the desired format with three decimal places
        for site in sites_info :
            li_conc = float(sites_info[ site ][ 'ini_Li' ])
            sites_info[ site ][ 'ini_Li' ] = f"{site} ({li_conc:.3f} wt. %)"

        # Sort the sites first by country, then by Li concentration within each country
        combined_data = {sites_info[ site ][ 'ini_Li' ] : {'IPCC' : matched_results[ site ][ 'IPCC' ],
                                                           'AWARE' : matched_results[ site ][ 'AWARE' ],
                                                           'country' : sites_info[ site ][ 'country_location' ],
                                                           'technology_group' : sites_info[ site ][ 'technology_group' ],
                                                           'activity_status': sites_info[ site ][ 'activity_status' ],
                                                           'activity_status_order' : sites_info[site]['activity_status_order']
                         }
                         for site in matched_results}

        sorted_data = sorted(
            combined_data.items(),
            key=lambda x : (
                x[1]['activity_status_order'],
                #x[1]['technology_group'],
                x[1]['country'],
                -float(x[0].split('(')[1].split(' wt.')[0].strip())
                )
            )

        # Extracting sorted data for the plot
        sorted_sites = [ site for site, _ in sorted_data ]
        ipcc_values = [ data[ 'IPCC' ] for _, data in sorted_data ]
        aware_values = [ data[ 'AWARE' ] for _, data in sorted_data ]

        # Creating subplots
        fig = make_subplots(rows=2, cols=1)

        # Adding IPCC subplot with no x-axis names and dark red color
        fig.add_trace(
            go.Bar(x=sorted_sites, y=ipcc_values, name='Climate change impacts', marker_color='rgb(139, 0, 0)'),
            row=1, col=1
            )
        # Remove x-axis labels for the first plot
        fig.update_xaxes(tickvals=[ ], row=1, col=1)

        # Adding AWARE subplot with blue color
        fig.add_trace(
            go.Bar(x=sorted_sites, y=aware_values, name='Water scarcity impacts', marker_color='rgb(0, 0, 139)'),
            row=2, col=1
            )

        # Customizing the layout to accommodate the larger plot and other requirements
        font_family = "Arial"
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=font_family, size=14, color='black'),
            title='LCA Results per Site (Grouped by Country)',
            showlegend=False,
            legend=dict(title='Impact Type', x=1.05, y=1, bgcolor='rgba(255, 255, 255, 1)', bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True, l=100, r=20, t=110, b=70),
            autosize=False,
            width=1200,  # Adjust the width to your preference
            height=600,  # Adjust the height to your preference
            )

        # Update axes properties to add grids, lines, and ticks
        axis_settings = dict(
            showgrid=True, gridwidth=1, gridcolor='lightgrey', zeroline=False, showline=True,
            linecolor='black', linewidth=2, ticks='outside', tickwidth=2, ticklen=5,
            tickfont=dict(family=font_family, size=12, color='black')
            )

        fig.update_xaxes(axis_settings)
        fig.update_yaxes(axis_settings, title_text="kg CO2eq/ kg Li2CO3", row=1, col=1)
        fig.update_yaxes(axis_settings, title_text="m3 world eq/kg Li2CO3", row=2, col=1)

        # Add text labels for impact types
        fig.add_annotation(text="Climate change impacts", xref="paper", yref="paper", x=1, y=0.95, showarrow=False)
        fig.add_annotation(text="Water scarcity impacts", xref="paper", yref="paper", x=1, y=0.45, showarrow=False)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check if save directory exists, if not, create it
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        # Save the figure to the specified directory
        save_path_png = os.path.join(save_dir, f'LCA_Comparison_technology_{timestamp}.png')
        fig.write_image(save_path_png)

        save_path_svg = os.path.join(save_dir, f'LCA_Comparison_technology_{timestamp}.svg')
        fig.write_image(save_path_svg)

        save_path_html = os.path.join(save_dir, f'LCA_Comparison_technology_{timestamp}.html')
        fig.write_html(save_path_html)

        print(f"Figure saved to {save_path_png} and {save_path_html}")

    def plot_LCA_results_comparison_based_on_exploration_and_Liconc(file_path,directory_path,save_dir) :
        matched_results,sites_info = preparing_data_for_LCA_results_comparison(file_path,directory_path)

        # Sort the sites first by country, then by Li concentration within each country
        combined_data = {site : {'IPCC' : matched_results[site]['IPCC'],
                                 'AWARE' : matched_results[site]['AWARE'],
                                 'Li_conc' : sites_info[site]['ini_Li'],
                                 'country' : sites_info[site]['country_location'],
                                 'technology_group' : sites_info[site]['technology_group'],
                                 'activity_status' : sites_info[site]['activity_status'],
                                 'activity_status_order' : sites_info[site]['activity_status_order'],
                                 'production': sites_info[site]['production']
                                 }
                         for site in matched_results}

        sorted_data = sorted(
            combined_data.items(),
            key=lambda x : (
                x[1]['activity_status_order'],
                # x[1]['technology_group'],
                -x[1]['production'],
                -x[1]['Li_conc']
                )
            )

        # Extracting sorted data for the plot
        sorted_sites = [site for site,_ in sorted_data]
        ipcc_values = [data['IPCC'] for _,data in sorted_data]
        aware_values = [data['AWARE'] for _,data in sorted_data]
        li_conc_values = [data['Li_conc'] for _,data in sorted_data]

        # Define a mapping of technology groups to patterns
        technology_patterns = {
            'geo_DLE' : '/',
            'salar_conv' : '\\',
            'salar_IX' : 'x',
            'salar_DLE' : '-'
            }

        # Creating subplots
        fig = make_subplots(rows=2,cols=1,shared_xaxes=True,
                            specs=[[{"secondary_y" : True}],[{"secondary_y" : True}]])

        # Iterate over the sorted data to add each bar individually to apply patterns
        for site,data in sorted_data :
            tech_group = sites_info[site.split(' (')[0]]['technology_group']  # Extract technology group for the site
            pattern_shape = technology_patterns.get(tech_group,None)  # Get the pattern for the technology group

            # Adding IPCC subplot bar with pattern
            fig.add_trace(
                go.Bar(x=[site],y=[data['IPCC']],name='Climate change impacts',
                       marker=dict(color='rgb(184, 145, 95)',pattern_shape=pattern_shape)),
                row=1,col=1,secondary_y=False
                )

            # Adding AWARE subplot bar with pattern
            fig.add_trace(
                go.Bar(x=[site],y=[data['AWARE']],name='Water scarcity impacts',
                       marker=dict(color='rgb(97, 104, 91)',pattern_shape=pattern_shape)),
                row=2,col=1,secondary_y=False
                )
        # # Adding IPCC subplot
        # fig.add_trace(
        #     go.Bar(x=sorted_sites,y=ipcc_values,name='Climate change impacts',marker_color='rgb(184, 145, 95)'),
        #     row=1,col=1,secondary_y=False
        #     )

        # Adding Li-conc as diamonds on the secondary y-axis for IPCC
        fig.add_trace(
            go.Scatter(x=sorted_sites,y=li_conc_values,name='Li concentration',mode='markers',
                       marker=dict(symbol='diamond',size=8,color='black')),
            row=1,col=1,secondary_y=True
            )

        # # Adding AWARE subplot
        # fig.add_trace(
        #     go.Bar(x=sorted_sites,y=aware_values,name='Water scarcity impacts',marker_color='rgb(97, 104, 91)'),
        #     row=2,col=1,secondary_y=False
        #     )

        # Adding Li-conc as diamonds on the secondary y-axis for AWARE
        fig.add_trace(
            go.Scatter(x=sorted_sites,y=li_conc_values,name='Li concentration',mode='markers',
                       marker=dict(symbol='diamond',size=8,color='rgb(7, 30, 39)')),
            row=2,col=1,secondary_y=True
            )

        # Customizing the layout to accommodate the larger plot and other requirements
        font_family = "Arial"
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=font_family,size=14,color='black'),
            title='LCA Results per Site (Grouped by Country)',
            showlegend=False,
            legend=dict(title='Impact Type',x=1.05,y=1,bgcolor='rgba(255, 255, 255, 1)',bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True,l=100,r=20,t=110,b=70),
            autosize=False,
            width=1200,  # Adjust the width to your preference
            height=600,  # Adjust the height to your preference
            )

        # Update axes properties to add grids, lines, and ticks
        axis_settings = dict(
            showgrid=False,gridwidth=1,gridcolor='lightgrey',zeroline=False,showline=True,
            linecolor='black',linewidth=2,ticks='outside',tickwidth=2,ticklen=5,
            tickfont=dict(family=font_family,size=12,color='black')
            )

        fig.update_xaxes(axis_settings)
        fig.update_yaxes(axis_settings,title_text="kg CO2eq/ kg Li2CO3",row=1,col=1)
        fig.update_yaxes(axis_settings,title_text="m3 world eq/kg Li2CO3",row=2,col=1)

        # Update y-axis labels for secondary y-axes
        fig.update_yaxes(title_text="Li conc.(wt. %)",row=1,col=1,secondary_y=True)
        fig.update_yaxes(title_text="Li conc. (wt. %)",row=2,col=1,secondary_y=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check if save directory exists, if not, create it
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        # Save the figure to the specified directory
        save_path_png = os.path.join(save_dir,f'LCA_Comparison_exploration_Li_conc_{timestamp}.png')
        fig.write_image(save_path_png)

        save_path_svg = os.path.join(save_dir,f'LCA_Comparison_exploration_Li_conc_{timestamp}.svg')
        fig.write_image(save_path_svg)

        save_path_html = os.path.join(save_dir,f'LCA_Comparison_exploration_Li_conc_{timestamp}.html')
        fig.write_html(save_path_html)

        print(f"Figure saved to {save_path_png} and {save_path_html}")




    def plot_LCA_results_comparison_based_on_production_and_Liconc(file_path,directory_path,save_dir) :
        matched_results,sites_info = preparing_data_for_LCA_results_comparison(file_path,directory_path)

        # Sort the sites first by country, then by Li concentration within each country
        combined_data = {site : {
            'IPCC' : matched_results[site]['IPCC'],
            'AWARE' : matched_results[site]['AWARE'],
            'Li_conc' : sites_info[site]['ini_Li'],
            'country' : sites_info[site]['country_location'],
            'technology_group' : sites_info[site]['technology_group'],
            'activity_status' : sites_info[site]['activity_status'],
            'activity_status_order' : sites_info[site]['activity_status_order'],
            'production' : sites_info[site]['production']
            }
                         for site in matched_results}

        sorted_data = sorted(
            combined_data.items(),
            key=lambda x : (
                x[1]['activity_status_order'],
                # x[1]['technology_group'],
                -x[1]['production'],
                #x[1]['country'],
                -x[1]['Li_conc']
                )
            )

        # Extracting sorted data for the plot
        sorted_sites = [site for site,_ in sorted_data]
        ipcc_values = [data['IPCC'] for _,data in sorted_data]
        aware_values = [data['AWARE'] for _,data in sorted_data]
        li_conc_values = [data['Li_conc'] for _,data in sorted_data]
        max_li_conc_value = max(li_conc_values)
        max_production_value = max(data['production'] for _,data in sorted_data if data['production'] > 0)
        max_y_value_ipcc = max(ipcc_values) * 1.3  # For example, 20% higher than the max value
        max_y_value_aware = max(aware_values) * 1.3  # Same for AWARE

        # Define a mapping of technology groups to patterns
        technology_patterns = {
            'geo_DLE' : 'rgb(197, 182, 120)',
            'salar_conv' : 'rgb(140, 124, 68)',
            'salar_IX' : 'rgb(126, 169, 158)',
            'salar_DLE' : 'rgb(185, 113, 54)'
            }

        # Creating subplots
        fig = make_subplots(rows=2,cols=1,shared_xaxes=True,
                            specs=[[{"secondary_y" : True}],[{"secondary_y" : True}]])

        # Calculate the total production
        total_production = sum(data['production'] for _,data in sorted_data if data['production'] > 0)

        # Calculate the starting x position for each site's bar
        cumulative_production = 0

        # Store the midpoint x-positions for the diamonds here
        midpoint_x_positions = []


        for site,data in sorted_data :
            sites_info[site]['start_pos'] = cumulative_production
            cumulative_production += data['production'] / total_production  # Increment the cumulative production

        for site,data in sorted_data :
            # The x position is the midpoint of the bar
            x_pos = (sites_info[site]['start_pos'] + (data['production'] / total_production) / 2)

            # The width of the bar is the production proportion
            bar_width = data['production'] / total_production

            midpoint_x_positions.append(x_pos)  # Store the midpoint position for the scatter plot

            cumulative_production += bar_width  # Increment the cumulative production

            tech_group = sites_info[site.split(' (')[0]]['technology_group']  # Extract technology group for the site
            pattern_shape = technology_patterns.get(tech_group,None)  # Get the pattern for the technology group


            # Adding IPCC subplot bar
            fig.add_trace(
                go.Bar(x=[x_pos],y=[data['IPCC']],width=[bar_width],name='Climate change impacts',
                       marker=dict(color=pattern_shape)),
                row=1,col=1
                )


            # Adding AWARE subplot bar
            fig.add_trace(
                go.Bar(x=[x_pos],y=[data['AWARE']],width=[bar_width],name='Water scarcity impacts',
                       marker = dict(color = pattern_shape)),
                row=2,col=1
                )



            fig.add_annotation(
                x=x_pos,  # Single value for the x position
                y=max_y_value_ipcc,  # Single value for the IPCC y position
                text=sites_info[site]['abbreviation'],  # The site name
                showarrow=False,
                xanchor="center",
                #textangle=90,
                font=dict(size=9),
                row=1,
                col=1
                )


        # Adding Li-conc as diamonds on the secondary y-axis for IPCC
        fig.add_trace(
            go.Scatter(x=midpoint_x_positions,y=li_conc_values,name='Li concentration',mode='markers',
                       marker=dict(symbol='diamond',size=8,color='black')),
            row=1,col=1,secondary_y=True
            )

        # Adding Li-conc as diamonds on the secondary y-axis for AWARE
        fig.add_trace(
            go.Scatter(x=midpoint_x_positions,y=li_conc_values,name='Li concentration',mode='markers',
                       marker=dict(symbol='diamond',size=8,color='rgb(7, 30, 39)')),
            row=2,col=1,secondary_y=True
            )

        # Customizing the layout to accommodate the larger plot and other requirements
        font_family = "Arial"

        fig.update_annotations(
            dict(
                xref="x",
                yref="y",
                valign="bottom",
                font=dict(size=9)
                )
            )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=font_family,size=14,color='black'),
            title='LCA Results per Site (based on production)',
            showlegend=False,
            legend=dict(title='Impact Type',x=1.05,y=1,bgcolor='rgba(255, 255, 255, 1)',bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True,l=100,r=20,t=110,b=70),
            autosize=False,
            width=1200,  # Adjust the width to your preference
            height=600,  # Adjust the height to your preference
            )

        # Update axes properties to add grids, lines, and ticks
        axis_settings = dict(
            showgrid=False,gridwidth=1,gridcolor='lightgrey',zeroline=False,showline=True,
            linecolor='black',linewidth=2,ticks='outside',tickwidth=2,ticklen=5,
            tickfont=dict(family=font_family,size=12,color='black')
            )

        fig.update_xaxes(axis_settings)
        fig.update_yaxes(axis_settings,  range=[0, max_y_value_ipcc], title_text="kg CO2eq/ kg Li2CO3",row=1,col=1)
        fig.update_yaxes(axis_settings,range=[0, max_y_value_aware],title_text="m3 world eq/kg Li2CO3",row=2,col=1)

        # Update y-axis labels for secondary y-axes
        fig.update_yaxes(range = [0, max_li_conc_value + 0.02], title_text="Li conc.(wt. %)",row=1,col=1,secondary_y=True)
        fig.update_yaxes(range = [0, max_li_conc_value + 0.02], title_text="Li conc. (wt. %)",row=2,col=1,secondary_y=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check if save directory exists, if not, create it
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        # Save the figure to the specified directory
        save_path_png = os.path.join(save_dir,f'LCA_Comparison_production_Li_conc_{timestamp}.png')
        fig.write_image(save_path_png)

        save_path_svg = os.path.join(save_dir,f'LCA_Comparison_production_Li_conc_{timestamp}.svg')
        fig.write_image(save_path_svg)

        save_path_html = os.path.join(save_dir,f'LCA_Comparison_production_Li_conc_{timestamp}.html')
        fig.write_html(save_path_html)

        print(f"Figure saved to {save_path_png}, {save_path_svg} and {save_path_html}")

    def plot_LCA_results_bubble_IPCC_AWARE(file_path,directory_path,save_dir) :
        matched_results,sites_info = preparing_data_for_LCA_results_comparison(file_path,directory_path)

        # Extracting data for the plot
        scatter_data = [{
            'site' : site,
            'IPCC' : matched_results[site]['IPCC'],
            'AWARE' : matched_results[site]['AWARE'],
            'Li_concentration' : info['ini_Li'],
            'Technology_Group' : info['technology_group']
            } for site,info in sites_info.items() if site in matched_results]

        # Creating the scatter plot
        fig = make_subplots(rows=1,cols=1)

        # Group data by technology group to plot them with different markers
        for tech_group,group_data in pd.DataFrame(scatter_data).groupby('Technology_Group') :
            tech_group_data = group_data.to_dict('records')
            fig.add_trace(
                go.Scatter(
                    x=[d['IPCC'] for d in tech_group_data],
                    y=[d['AWARE'] for d in tech_group_data],
                    mode='markers',
                    marker=dict(
                        size=[d['Li_concentration'] for d in tech_group_data],
                        sizemode='area',
                        sizeref=2. * max([d['Li_concentration'] for d in tech_group_data]) / (40. ** 2),
                        sizemin=4
                        ),
                    name=tech_group
                    )
                )

        # Customizing the layout to accommodate the larger plot and other requirements
        font_family = "Arial"


        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=font_family,size=14,color='black'),
            title='Climate Change vs. Water Scarcity Impacts by Li-Concentration',
            xaxis_title='IPCC - Climate Change Impacts',
            yaxis_title='AWARE - Water Scarcity Impacts',
            showlegend=True,
            legend=dict(title='Impact Type',x=1.05,y=1,bgcolor='rgba(255, 255, 255, 1)',bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True,l=100,r=20,t=110,b=70),
            autosize=False,
            width=1200,  # Adjust the width to your preference
            height=600,  # Adjust the height to your preference
            )

        # Update axes properties to add grids, lines, and ticks
        axis_settings = dict(
            showgrid=True,gridwidth=1,gridcolor='lightgrey',zeroline=False,showline=True,
            linecolor='black',linewidth=2,ticks='outside',tickwidth=2,ticklen=5,
            tickfont=dict(family=font_family,size=12,color='black')
            )

        # Update layout
        fig.update_layout(
            title='Climate Change vs. Water Scarcity Impacts by Li-Concentration',
            xaxis_title='IPCC - Climate Change Impacts',
            yaxis_title='AWARE - Water Scarcity Impacts',
            legend_title='Technology Group'
            )

        fig.update_xaxes(axis_settings)
        fig.update_yaxes(axis_settings)

        # Save the figure
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        fig.write_image(os.path.join(save_dir,f'LCA_Results_Scatter_{timestamp}.png'))

        fig.write_image(os.path.join(save_dir,f'LCA_Results_Scatter_{timestamp}.svg'))

        fig.write_html(os.path.join(save_dir,f'LCA_Results_Scatter_{timestamp}.html'))

        print(f"Scatter plot saved in {save_dir}")


    def plot_LCA_results_scatter_Li_conc(file_path,directory_path,save_dir) :
        matched_results,sites_info = preparing_data_for_LCA_results_comparison(file_path,directory_path)

        # Extracting data for the plot
        scatter_data = [{
            'site' : site,
            'IPCC' : matched_results[site]['IPCC'],
            'AWARE' : matched_results[site]['AWARE'],
            'Li_concentration' : info['ini_Li'],
            'Technology_Group' : info['technology_group']
            } for site,info in sites_info.items() if site in matched_results]

        # Creating the scatter plot
        fig = make_subplots(rows=1,cols=1)

        # Group data by technology group to plot them with different markers
        for tech_group,group_data in pd.DataFrame(scatter_data).groupby('Technology_Group') :
            tech_group = sites_info[site.split(' (')[0]]['technology_group']  # Extract technology group for the site
            pattern_shape = technology_patterns.get(tech_group,None)  # Get the pattern for the technology group

            fig.add_trace(
                go.Scatter(
                    x=[d['IPCC'] for d in tech_group_data],
                    y=[d['AWARE'] for d in tech_group_data],
                    mode='markers',
                    marker=dict(
                        size=[d['Li_concentration'] for d in tech_group_data],
                        sizemode='area',
                        sizeref=2. * max([d['Li_concentration'] for d in tech_group_data]) / (40. ** 2),
                        sizemin=4
                        ),
                    name=tech_group
                    )
                )

        # Customizing the layout to accommodate the larger plot and other requirements
        font_family = "Arial"

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=font_family,size=14,color='black'),
            title='Climate Change vs. Water Scarcity Impacts by Li-Concentration',
            xaxis_title='IPCC - Climate Change Impacts',
            yaxis_title='AWARE - Water Scarcity Impacts',
            showlegend=True,
            legend=dict(title='Impact Type',x=1.05,y=1,bgcolor='rgba(255, 255, 255, 1)',bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True,l=100,r=20,t=110,b=70),
            autosize=False,
            width=1200,  # Adjust the width to your preference
            height=600,  # Adjust the height to your preference
            )

        # Update axes properties to add grids, lines, and ticks
        axis_settings = dict(
            showgrid=True,gridwidth=1,gridcolor='lightgrey',zeroline=False,showline=True,
            linecolor='black',linewidth=2,ticks='outside',tickwidth=2,ticklen=5,
            tickfont=dict(family=font_family,size=12,color='black')
            )

        # Update layout
        fig.update_layout(
            title='Climate Change vs. Water Scarcity Impacts by Li-Concentration',
            xaxis_title='IPCC - Climate Change Impacts',
            yaxis_title='AWARE - Water Scarcity Impacts',
            legend_title='Technology Group'
            )

        fig.update_xaxes(axis_settings)
        fig.update_yaxes(axis_settings)

        # Save the figure
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        fig.write_image(os.path.join(save_dir,f'LCA_Results_Scatter_{timestamp}.png'))

        fig.write_image(os.path.join(save_dir,f'LCA_Results_Scatter_{timestamp}.svg'))

        fig.write_html(os.path.join(save_dir,f'LCA_Results_Scatter_{timestamp}.html'))

        print(f"Scatter plot saved in {save_dir}")


    def plot_LCA_results_scatter_Li_conc(file_path,directory_path,save_dir) :
        matched_results,sites_info = preparing_data_for_LCA_results_comparison(file_path,directory_path)

        # Create a dataframe from the data
        scatter_data = [{
            'site' : site,
            'IPCC' : matched_results[site]['IPCC'],
            'AWARE' : matched_results[site]['AWARE'],
            'Li_concentration' : info['ini_Li'],
            'Technology_Group' : info['technology_group']
            } for site,info in sites_info.items() if site in matched_results]

        # Creating two subplots, one for IPCC and one for AWARE
        fig = make_subplots(rows=2,cols=1,subplot_titles=('IPCC vs. Li-Concentration','AWARE vs. Li-Concentration'))

        technology_patterns = {
            'geo_DLE' : 'rgb(197, 182, 120)',
            'salar_conv' : 'rgb(140, 124, 68)',
            'salar_IX' : 'rgb(126, 169, 158)',
            'salar_DLE' : 'rgb(185, 113, 54)'
            }

        for tech_group,group_df in pd.DataFrame(scatter_data).groupby('Technology_Group') :
            color = technology_patterns.get(tech_group,'rgb(0,0,0)')  # Default to black if not found

            fig.add_trace(
                go.Scatter(
                    x=group_df['Li_concentration'],
                    y=group_df['IPCC'],
                    mode='markers',
                    marker=dict(size=14,color=color),
                    name=f'IPCC - {tech_group}',
                    text=group_df['site']  # Site name on hover
                    ),
                row=1,
                col=1
                )

            fig.add_trace(
                go.Scatter(
                    x=group_df['Li_concentration'],
                    y=group_df['AWARE'],
                    mode='markers',
                    marker=dict(size=14,color=color),
                    name=f'AWARE - {tech_group}',
                    text=group_df['site']  # Site name on hover
                    ),
                row=2,
                col=1
                )

        # Customizing the layout to accommodate the larger plot and other requirements
        font_family = "Arial"

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family=font_family,size=14,color='black'),
            title='Climate Change vs. Water Scarcity Impacts by Li-Concentration',
            xaxis_title='IPCC - Climate Change Impacts',
            yaxis_title='AWARE - Water Scarcity Impacts',
            showlegend=True,
            legend=dict(title='Impact Type',x=1.05,y=1,bgcolor='rgba(255, 255, 255, 1)',bordercolor='black',
                        borderwidth=1),
            margin=dict(autoexpand=True,l=100,r=20,t=110,b=70),
            autosize=False,
            width=1200,  # Adjust the width to your preference
            height=600,  # Adjust the height to your preference
            )

        # Update axes properties to add grids, lines, and ticks
        axis_settings = dict(
            showgrid=True,gridwidth=1,gridcolor='lightgrey',zeroline=False,showline=True,
            linecolor='black',linewidth=2,ticks='outside',tickwidth=2,ticklen=5,
            tickfont=dict(family=font_family,size=12,color='black')
            )

        # Update layout
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="LCA Results Scatter Plot"
            )

        # Update xaxis properties
        fig.update_xaxes(axis_settings,title_text='Li-Concentration (wt.%)',row=1,col=1)
        fig.update_xaxes(axis_settings,title_text='Li-Concentration (wt.%)',row=2,col=1)

        # Update yaxis properties
        fig.update_yaxes(axis_settings, title_text='IPCC (kg CO2eq/kg Li2CO3)',row=1,col=1)
        fig.update_yaxes(axis_settings, title_text='AWARE (m³ world eq/kg Li2CO3)',row=2,col=1)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        fig.write_image(os.path.join(save_dir,f'LCA_Results_Scatter_Liconc_{timestamp}.png'))

        fig.write_image(os.path.join(save_dir,f'LCA_Results_Scatter_Liconc_{timestamp}.svg'))

        fig.write_html(os.path.join(save_dir,f'LCA_Results_Scatter_Liconc_{timestamp}.html'))

        print(f"Scatter plot saved in {save_dir}")



    def create_plots_from_brinechemistry(directory_path, save_dir) :
        # Dictionary to hold the aggregated data for each site
        site_data = {}


        # Process each CSV file in the directory
        for file in os.listdir(directory_path) :
            if file.endswith('.csv') :
                # Extract site abbreviation from the file name
                site_abbreviation = file.split('_')[0]

                # Load the CSV file
                file_path = os.path.join(directory_path,file)
                csv_data = pd.read_csv(file_path)

                # Aggregate data by site
                if site_abbreviation not in site_data :
                    site_data[site_abbreviation] = {'Li-conc' : [],'IPCC' : [],'AWARE' : []}

                for _,row in csv_data.iterrows() :
                    site_data[site_abbreviation]['Li-conc'].append(row['Li-conc'])
                    site_data[site_abbreviation]['IPCC'].append(row['IPCC'])
                    site_data[site_abbreviation]['AWARE'].append(row['AWARE'])



        fig = make_subplots(rows=2,cols=1,subplot_titles=("Climate Change Impact","Water Scarcity Impact"))

        # Generate a list of unique colors for each site
        colors = px.colors.qualitative.Antique
        color_map = {site : colors[i % len(colors)] for i,site in enumerate(site_data.keys())}

        # Create subplots for each site
        for site,data in site_data.items() :


            # Add scatter plot for climate change impact
            fig.add_trace(go.Scatter(x=data['Li-conc'],y=data['IPCC'],mode='markers', name=site,
                                 marker=dict(color=color_map[site])),row=1,col=1)

            # Add scatter plot for water scarcity impact
            fig.add_trace(go.Scatter(x=data['Li-conc'],y=data['AWARE'],mode='markers', name=site,
                                 marker=dict(color=color_map[site])),row=2,col=1)

        # Update layout
        fig.update_layout(height=600,width=800,title_text=f"Impacts for {site}")
        fig.update_xaxes(range=[0, 0.4], title_text="Li-conc (weight %)",row=1,col=1)
        fig.update_xaxes(range=[0, 0.4],title_text="Li-conc (weight %)",row=2,col=1)
        fig.update_yaxes(range = [0, 100], title_text="IPCC",row=1,col=1)
        fig.update_yaxes(range = [0, 40], title_text="AWARE",row=2,col=1)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check if save directory exists, if not, create it
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        # Save the figure to the specified directory
        save_path_png = os.path.join(save_dir,f'LCA_Brinechemistry_{timestamp}.png')
        fig.write_image(save_path_png)

        save_path_svg = os.path.join(save_dir,f'LCA_Brinechemistry_{timestamp}.svg')
        fig.write_image(save_path_svg)

        save_path_html = os.path.join(save_dir,f'LCA_Brinechemistry_{timestamp}.html')
        fig.write_html(save_path_html)

        print(f"Figure saved to {save_path_png} and {save_path_html}")


    def create_waterfall_plots(file_path, save_dir, abbrev_loc, li_conc, eff, impact_type, location) :
        df = prepare_data_for_waterfall_diagram(file_path)

        # Reverse the DataFrame to start with the last process
        reversed_df = df.iloc[: :-1].reset_index(drop=True)

        # Remove text in brackets from the 'Activity' column for cleaner display
        reversed_df['Activity'] = reversed_df['Activity'].str.replace(r"\(.*\)","",regex=True).str.strip()

        # Calculate the score differences which will be the height of each bar
        reversed_df['Score_Diff'] = reversed_df['Score'].diff().fillna(reversed_df['Score'].iloc[0])

        # Calculate the 'Start' column representing where each bar starts on the y-axis
        reversed_df['Start'] = reversed_df['Score_Diff'].cumsum() - reversed_df['Score_Diff']

        # Initialize a waterfall chart
        fig = go.Figure()

        # Define your color map for each category
        category_color_map = {
            'Heat' : '#d89000',
            'Electricity' : '#4287f5',
            'Chemicals' : '#4f9d69',
            'Rest' : '#a8887f'
            }

        # Add bars to the chart
        for index,row in reversed_df.iterrows() :
            base = row['Start'] if index > 0 else 0

            # Iterate over each category within a process to create segments
            for category,score in row['Category_Scores'].items() :
                color = category_color_map.get(category,'#000000')  # Default to black if category not found
                fig.add_trace(go.Bar(
                    name=f"{row['Activity']} - {category}",
                    x=[row['Activity']],
                    y=[score],
                    base=[base],
                    marker_color=color,  # Use the color mapping
                    hoverinfo="name+y+text",
                    textposition="outside"
                    ))

                # Update base for the next category
                base += score

        # Customize layout
        fig.update_layout(
            title=f"Process Contributions to Total Score {impact_type} - {location}",
            barmode='stack',
            showlegend=False,
            plot_bgcolor='white',
            xaxis=dict(
                showline=True,
                linewidth=1,
                linecolor='black',
                mirror=True,
                tickmode='linear',
                tickfont=dict(family='Arial',color='black',size=12),
                ticklen=10,
                tickwidth=2
                ),
            yaxis=dict(
                showline=True,
                linewidth=1,
                linecolor='black',
                mirror=True,
                zeroline=False,
                tickmode='array',
                tickfont=dict(family='Arial',color='black',size=15),
                tickvals=[i * 10 for i in range(int(reversed_df['Score'].max() / 10) + 1)],
                dtick=10,
                ticklen=10,
                tickwidth=2,
                range = [0, reversed_df['Start'].max() + reversed_df['Score_Diff'].max()]

                ),
            font=dict(size=12),
            bargap=0
            )

        fig.update_xaxes(ticks="outside")
        fig.update_yaxes(ticks="outside",tickvals=[i * 10 for i in range(int(reversed_df['Score'].max() / 10) + 1)])

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check if save directory exists, if not, create it
        if not os.path.exists(save_dir) :
            os.makedirs(save_dir)

        # Save the figure to the specified directory
        save_path_png = os.path.join(save_dir,f'LCA_contributional_analysis_{impact_type}_{abbrev_loc}_{li_conc}_{eff}_{timestamp}.png')
        fig.write_image(save_path_png)

        save_path_svg = os.path.join(save_dir,f'LCA_contributional_analysis_{impact_type}_{abbrev_loc}_{li_conc}_{eff}_{timestamp}.svg')
        fig.write_image(save_path_svg)

        #save_path_html = os.path.join(save_dir,f'LCA_contributional_analysis_{impact_type}_{abbrev_loc}_{li_conc}_{eff}_{timestamp}.html')
        #fig.write_html(save_path_html)

        print(f"Figure saved as png and svg files.")

    def process_data_based_on_excel(excel_path,base_directory, save_directory) :
        excel_data = pd.read_excel(excel_path)
        # Transpose the data for easier processing

        transposed_data = excel_data.transpose()

        # Set the first row as the header

        transposed_data.columns = transposed_data.iloc[0]

        # Drop the first row since it's now the header

        excel_data = transposed_data.drop(transposed_data.index[0])

        for index,row in excel_data.iterrows() :
            abbrev_loc = row['abbreviation']
            li_conc = round(row['ini_Li'],3)
            eff = row['Li_efficiency']
            location = index

            target_directory = os.path.join(base_directory,f'results_{abbrev_loc}')

            for impact_type in ['climatechange','waterscarcity'] :
                latest_file_path = find_latest_matching_file(target_directory,li_conc,eff,impact_type)
                if latest_file_path :
                    print(f"Processing file: {latest_file_path}")
                    Visualization.create_waterfall_plots(latest_file_path,save_directory, abbrev_loc, li_conc, eff, impact_type, location)
                else :
                    print(f"No matching file found for {abbrev_loc}, {impact_type} with Li_conc: {li_conc} and efficiency: {eff}")


class GeneralGraphs:

    @staticmethod
    def create_global_map(save_dir, data, longitude_col='longitude', latitude_col='latitude', name_col='Site name'):
        """
        Creates a global map of sites using Plotly.
        """
        try:
            global_map = go.Figure(go.Scattergeo(
                lon=data[longitude_col],
                lat=data[latitude_col],
                mode='markers',
                marker=dict(size=10, color='rgb(135,206,250)', line=dict(width=1, color='rgba(255,255,255,0.5)')),
                text=data[name_col],  # Display site name on hover
                hoverinfo='text'
            ))

            global_map.update_layout(
                title=dict(text='Global Distribution of Operations', x=0.5, font=dict(size=20, color='black')),
                geo=dict(
                    projection_type='natural earth',
                    showland=True,
                    landcolor='rgb(243,243,243)',
                    countrycolor='rgb(204,204,204)',
                    showcountries=True,
                    showcoastlines=True,
                    coastlinecolor='rgb(180,180,180)'
                )
            )

            GeneralGraphs._save_figure(global_map, save_dir, 'LCA_globalmap')

            return global_map
        except Exception as e:
            print(f"Error occurred: {e}")

    @staticmethod
    def create_submap(save_dir, data, region_bounds, longitude_col='longitude', latitude_col='latitude', name_col='Site name'):
        """
        Creates a submap for a specific region using Plotly.
        """
        try:
            submap = go.Figure(go.Scattergeo(
                lon=data[longitude_col],
                lat=data[latitude_col],
                mode='markers',
                marker=dict(size=10, color='rgb(255,69,0)', line=dict(width=1, color='rgba(255,255,255,0.5)')),
                text=data[name_col],  # Display site name on hover
                hoverinfo='text'
            ))

            submap.update_layout(
                title=dict(text='Detailed View of Specific Region', x=0.5, font=dict(size=20, color='black')),
                geo=dict(
                    projection_type='natural earth',
                    showland=True,
                    landcolor='rgb(243,243,243)',
                    countrycolor='rgb(204,204,204)',
                    lonaxis=dict(range=[region_bounds['lon_min'], region_bounds['lon_max']]),
                    lataxis=dict(range=[region_bounds['lat_min'], region_bounds['lat_max']])
                )
            )

            GeneralGraphs._save_figure(submap, save_dir, 'LCA_submap')

            return submap
        except Exception as e:
            print(f"Error occurred: {e}")

    @staticmethod
    def _save_figure(figure, save_dir, base_filename):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            save_path_png = os.path.join(save_dir, f'{base_filename}_{timestamp}.png')
            figure.write_image(save_path_png)

            save_path_svg = os.path.join(save_dir, f'{base_filename}_{timestamp}.svg')
            figure.write_image(save_path_svg)
            #save_path_html = os.path.join(save_dir, f'{base_filename}_{timestamp}.html')
            #figure.write_html(save_path_html)
            print(f"Figure saved to {save_path_png} and {save_path_svg}")
        except Exception as e:
            print(f"Error saving figure: {e}")
