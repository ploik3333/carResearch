import matplotlib.pyplot as plt
import openmdao.api as om

from util import *

RUN: bool = True

# find all csv files, so doesnt have to be hard-coded
csv_files: list[Path] = getFiles('./data/attack') if RUN else []

# using matplotlib
if len(csv_files) > 0:
    fig, axes = plt.subplots(nrows=max(1, len(csv_files)), ncols=3, layout="constrained")

# loop through all csv files / Main Loop
for i, file in enumerate(csv_files):
    # e  (epsilon) : 1.1000
    # w1 (window 1): 10
    # l  (window 2): 100
    # fl (frame len): 5
    datadict = calculate_data(file, e = 1.1, w1 = 1.1, l = 100, fl = 5, cache=False)
    # print(datadict)

    axes[i][0].set_title(file)
    axes[i][1].set_title("Ratios of avgs")
    axes[i][2].set_title("'RUC's (sum of outliers)")


    # plot length of time between each ecu broadcast
    axes[i][0].plot(range(1, len(datadict['timediffs'])+1), datadict["timediffs"])
    # plot ratios
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), datadict['ratio'])
    # plot RUC
    axes[i][2].scatter(range(1, len(datadict['RUCs']) + 1), datadict['RUCs'], s=1)
    # plot ratio of RUCs
    # axes[i][3].plot(range(1, len(datadict['RRUCs']) + 1), datadict['RRUCs'])


    # plot upper and lower bounds
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMhigh'] for _ in range(len(datadict['ratio']))])
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMlow'] for _ in range(len(datadict['ratio']))])

    i+=1

print("done")
if len(csv_files) > 0:
    plt.show()



# ttd < .5
# md <= .55

from optimize import runoptimizer
# runoptimizer()



"""
 e  (Threshold) : 5.4613
  w1 (Weight)    : 0.0362  (w2 = 0.9638)
  l  (Window)    : 149
  fl (Frame Len) : 1
  """