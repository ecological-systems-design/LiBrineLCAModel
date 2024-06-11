from pathlib import Path
import pickle
import os
from src.Postprocessing_results.visualization_functions import Visualization

if not os.path.exists("results") :
    os.mkdir("results")

if __name__ == '__main__' :

    # Replace this path with the path to your .pkl file
    file_path = 'C:\\Users\\Schenker\\PycharmProjects\\Geothermal_brines\\results_dict_Ata_0.05_0.30000000000000016.pkl'

    # Open the file in binary read mode
    with open(file_path, 'rb') as file:
        # Load data from the file
        data = pickle.load(file)

    # Now you can use the 'data' variable which contains the deserialized data
    print(data)

    # Create Sankey diagram
    Visualization.create_sankey_diagram(data, r"C:\Users\Schenker\PycharmProjects\Geothermal_brines\results\rawdata", "Ata", 0.9, 0.25)
