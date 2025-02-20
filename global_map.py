import pandas as pd
import plotly.graph_objects as go
from src.Postprocessing_results.visualization import *

if __name__ == '__main__' :
    file_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\Brinesites_model.csv'
    save_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\global_comparison'
    data = pd.read_csv(file_path,delimiter=';')

    GeneralGraphs.create_global_map(save_dir,data)

    # Set the regional bounds for the targeted area
    region_bounds = {
        'lon_min' : -70,  # Extended to include areas slightly further west
        'lon_max' : -65.8,  # Kept the same to maintain focus on the eastern parts
        'lat_min' : -28,  # Extended south to include Maricunga
        'lat_max' : -20  # Northern boundary kept the same
        }

GeneralGraphs.create_submap(save_dir, data, region_bounds)