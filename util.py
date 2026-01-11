# from typing import Tuple, Generator, Any, overload
import numpy as np
import math
from pathlib import Path
from utila import *



#useful simple functions
safediv = lambda a: 0 if a == 0 else 1/a # no divide by zero, 1/0 is 0 here
harmonic = lambda a: len(a) * safediv(sum(map(safediv, a)))              #len(a)/sum(map(safediv,a))
arithmetic = avg = lambda a: sum(a)/len(a)
R = lambda x: harmonic(x) * safediv(arithmetic(x))                                 #harmonic(x)/arithmetic(x)


@calc_cache
def calculate_data(file, e=2.7, window_size=50, fl = 9, threshold = 0.00):

    # get differences in times and direct data from file
    timediffs, attack = read(file)
    # print(timediffs[:10])

    # calculate and display ratios
    ratios_of = lambda data: [R(data[i:j]) for i,j in window(0,len(timediffs), window_size, include_extra=False)]
    ratios = ratios_of(timediffs)
    # print(ratios[:10])

    mean = avg(ratios)
    std_dev = math.sqrt(sum([(x-mean)**2 for x in ratios])/(len(ratios)-1))
    print(f"{std_dev = }")

    SMhigh = mean + e * std_dev
    SMlow = mean - e * std_dev
    print(f"{SMhigh = }")
    print(f"{SMlow = }")


    def RUC(T, _fl):
        # fl is frame length
        total = 0
        for i in range(max(0, T-_fl), T+1):
            point = ratios[i]
            if point > SMhigh:   # center about zero
                total += point - SMhigh
            elif point < SMlow:
                total += point - SMlow
            else:
                total += 0 # only add outliers
        return total
    def first_detected(data, start = 0):
        for i,v in enumerate(data[start:]):
            if v > threshold:
                return i+start
        if start >= len(data):
            return start
        return i+start


    # sigmoid = lambda x, T=0.04, k=300: 1/(1+e**(-k*(x-T)))


    RUCs = [RUC(T, fl) for T in range(len(ratios))]
    # RRUCs = [sigmoid(T, T=SMhigh) for T in ratios]
    # RRUCs = [RUCs[i:j] for i,j in window(0, len(RUCs), window_size, include_extra=False)]


    if attack:
        first_attack = attack.index(1)
        time_to_detection = first_detected(RUCs, start=first_attack) - first_attack
        false_alarm = sum([v > threshold for i,v in enumerate(RUCs) if attack[i] == 0])
        missed = sum([v <= threshold for i,v in enumerate(RUCs) if attack[i] == 1])

        print(f"{first_attack=}")
        print(f"{time_to_detection=}")
        print(f"{false_alarm=}")
        print(f"{missed=}")
    else:
        first_attack = 0
        time_to_detection = 0
        false_alarm = 0
        missed = 0



    #  the most important is the false alarm count, time to detection, and last the missed detection rate.
    return {'SMlow':SMlow, 'SMhigh':SMhigh, 'mean':mean, 'ratio':ratios, 'std_dev':std_dev, 'timediffs': timediffs, 'RUCs':RUCs, "ttd": time_to_detection, "fa": false_alarm, 'md': missed  }
