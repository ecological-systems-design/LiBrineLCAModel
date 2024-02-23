import pandas as pd
import plotly.graph_objects as go
from rsc.Postprocessing_results.visualization_functions import *

if __name__ == '__main__' :
    file_path = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\data\Brinesites_model.csv'
    save_dir = r'C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\figures\global_comparison'
    data = pd.read_csv(file_path,delimiter=';')

    Visualization.create_global_map(save_dir,data)

    region_bounds = {
        'lon_min' : -73,
        'lon_max' : -65,
        'lat_min' : -30,
        'lat_max' : -20
        }

    Visualization.create_submap(save_dir, data, region_bounds)