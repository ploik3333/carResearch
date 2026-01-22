import matplotlib.pyplot as plt

from util import *

import optimize
RUN: bool = False

# find all csv files, so doesnt have to be hard-coded
csv_files: list[Path] = getFiles('./data/attack') if RUN else []

# using matplotlib
if len(csv_files) > 0:
    fig, axes = plt.subplots(nrows=max(1, len(csv_files)), ncols=3, layout="constrained")

# loop through all csv files / Main Loop
for i, file in enumerate(csv_files):
    datadict = calculate_data(file, e = 1, w1 = 0.80, l = 150, fl = 110, cache=False)

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


# print("LB avg", avg(list(map(lambda x:x[0], thresholds))))
# print("UB avg", avg(list(map(lambda x:x[1], thresholds))))
# """ # BEST computed averages over a period
# LB avg -0.01383645104947388
# UB avg 0.12008719296491677
# """



# ttd < .5
# md <= .55






""" # initially found values - bad
 e    : 5.4613
  w1  : 0.0362  (w2 = 0.9638)
  l   : 149
  fl  : 1
  """
