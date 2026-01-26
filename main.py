import matplotlib.pyplot as plt
import numpy as np

from util import *
log_time_setup()


# import optimize
RUN: bool = 4


# using matplotlib
if RUN: #len(csv_files) > 0:
    fig, axes = plt.subplots(nrows=max(1, RUN), ncols=3, layout="constrained")

# loop through all csv files / Main Loop
for i in range (RUN): #, file in enumerate(csv_files):
    file = getFiles('./data/attack')[i]
    benign = getFiles('./data/benign')[i]
    datadict = evaluate(file, benign, e=3.96, w1=0.27, fl=5, l=32, simple = False)
    value = lambda a: datadict[a]
    print(f"Calculating f{file}")
    print(f"{value('fa')=}")
    print(f"{value('ttd')=}")
    print(f"{value('md')=}")


    axes[i][0].set_title(f"{file}")
    axes[i][1].set_title("Ratios of avgs")
    axes[i][2].set_title("'RUC's (sum of outliers)")

    # plot length of time between each ecu broadcast
    axes[i][0].plot(range(1, len(datadict['timediffs'])+1), datadict["timediffs"])
    # plot ratios
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), datadict['ratio'])
    # plot RUC
    axes[i][2].scatter(range(1, len(datadict['RUCs']) + 1), datadict['RUCs'], s=1)

    # plot upper and lower bounds
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMhigh'] for _ in range(len(datadict['ratio']))], color='orange')
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMlow'] for _ in range(len(datadict['ratio']))], color='green')
    axes[i][2].plot(range(1, len(datadict['ratio']) + 1), [datadict['thresholds'][1] for _ in range(len(datadict['ratio']))], color='orange')
    axes[i][2].plot(range(1, len(datadict['ratio']) + 1),[datadict['thresholds'][0] for _ in range(len(datadict['ratio']))], color='green')

print("done")
if RUN: #len(csv_files) > 0:
    plt.show()


# Results from one trial (DOS ATTACK)
# e=4.66, w1=0.82, fl=111, l=152
# e=2.69, w1=0.92, fl=32,  l=9
# e=4.59, w1=0.03, fl=15, l=36