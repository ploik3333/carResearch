from typing import Tuple, Generator, Any, overload
import math
import scipy
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
# from pypdf import PdfReader
# import fitz
# import fontTools
# from scipy.optimize import minimize
import numpy as np
import openmdao.api as om
from util import *
from mpl_toolkits.mplot3d import axes3d


# find all csv files, so doesnt have to be hard-coded
csv_files: list[Path] = [Path('./data/') / Path(file) for file in os.listdir("./data") if Path(file).suffix == ".csv"]
# csv_files = []

# using matplotlib
fig, axes = plt.subplots(nrows=max(1, len(csv_files)), ncols=3, layout="constrained")

i: int = 0

# loop through all csv files / Main Loop
for file in csv_files:
    # print(f"calculating {file}")
    datadict = calculate_data(file, e = 2.7, cache=False)
    # print(datadict)

    axes[i][0].set_title(file)
    axes[i][1].set_title("Ratios of avgs")
    axes[i][2].set_title("'RUC's (sum outliers)")


    # plot length of time between each ecu broadcast
    axes[i][0].plot(range(1, len(datadict['timediffs'])+1), datadict["timediffs"])
    # plot ratios
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), datadict['ratio'])
    # plot RUC
    axes[i][2].plot(range(1, len(datadict['RUCs']) + 1), datadict['RUCs'])
    # plot ratio of RUCs
    # axes[i][3].plot(range(1, len(datadict['RRUCs']) + 1), datadict['RRUCs'])


    # plot upper and lower bounds
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMhigh'] for _ in range(len(datadict['ratio']))])
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMlow'] for _ in range(len(datadict['ratio']))])

    i+=1

print("done")
if len(csv_files) > 0:
    plt.show()



