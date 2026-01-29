import matplotlib.pyplot as plt
import numpy as np

import util
from util import *
log_time_setup()



RUN: int = 4

if not RUN:
    import optimize
    discord_log("DONE WITH OPTIMIZATION")

# using matplotlib
if RUN: #len(csv_files) > 0:
    fig, axes = plt.subplots(nrows=max(1, RUN), ncols=3, layout="constrained")

# loop through all csv files / Main Loop
for i in range (RUN): #, file in enumerate(csv_files):
    file = getFiles('./data/attack')[i]
    benign = getFiles('./data/benign')[i]
    print(f"Calculating f{file}")
    datadict = evaluate(file, benign, e=4.113917102694185, w1=1, fl=13, l=98, simple = False, verbose = True) # e=3.18, w1=0.00, fl=22, l=197 # e=3.46, w1=0.00, fl=8, l=25
    # e = 3.89, w1 = 0.87, fl = 95, l = 29   # e=2.66, w1=0.00, fl=5, l=49
    # fuzzing best # 4.002780265355079, 0.6604852293204866, 12, 5
    value = lambda a: datadict[a]
    print(f"{value('fa')=}", end=' ')
    print(f"{value('ttd')=}", end=' ')
    print(f"{value('md')=}")


    axes[i][0].set_title(f"{file}")
    axes[i][1].set_title("Ratios of avgs")
    axes[i][2].set_title("'RUC's (sum of outliers)")

    # plot length of time between each ecu broadcast
    axes[i][0].plot(range(1, len(datadict['timediffs'])+1), datadict["timediffs"])
    # plot which are actually attacks
    la = max(datadict['timediffs'])
    indexes = []

    attacks = [i for i,v in enumerate(datadict["attacks"]) if v] # only get attack indexes
    axes[i][0].scatter(attacks, [0]*len(attacks), s=3, color='red')
    # plot ratios
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), datadict['ratio'])
    # plot RUC
    axes[i][2].scatter(range(1, len(datadict['RUCs']) + 1), datadict['RUCs'], s=1)

    # plot upper and lower bounds
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMhigh'] for _ in range(len(datadict['ratio']))], color='orange')
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMlow'] for _ in range(len(datadict['ratio']))], color='green')
    axes[i][2].plot(range(1, len(datadict['ratio']) + 1), [datadict['thresholds'][1] for _ in range(len(datadict['ratio']))], color='orange')
    axes[i][2].plot(range(1, len(datadict['ratio']) + 1),[datadict['thresholds'][0] for _ in range(len(datadict['ratio']))], color='green')
    print("\n")
print("done")
if RUN: #len(csv_files) > 0:
    plt.show()
# Results from one trial (DOS ATTACK)
# e=4.66, w1=0.82, fl=111, l=152
# e=2.69, w1=0.92, fl=32,  l=9
# e=4.59, w1=0.03, fl=15, l=36

# BEST DOS
# e=3.50, w1=0.61, fl=20, l=31

# BEST FUZZING
# e = 3.89, w1 = 0.87, fl = 95, l = 29
# e=4.113917102694185, w1=1, fl=13, l=98

# BEST SYSTEMATIC
# e=4.716125702261129, w1=0.2484264492329204, fl=31, l=171
# e=2.681446700541124, w1=0.2718312306261839, fl=61, l=94

