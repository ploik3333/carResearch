import numpy as np
# from pulp import LpVariable
from utila import *

#useful simple functions
safediv = lambda a: 0 if a == 0 else 1/a # no divide by zero, 1/0 is 0 here
harmonic = lambda a: len(a) * safediv(sum(map(safediv, a)))              #len(a)/sum(map(safediv,a))
arithmetic = avg = lambda a: sum(a)/len(a)
R = lambda x: harmonic(x) * safediv(arithmetic(x))                                 #harmonic(x)/arithmetic(x)


def RUC(ratios, SMlow, SMhigh, l, _fl):
    # fl is frame length
    total = 0
    for i in range(max(0, l - _fl), l + 1):
        point = ratios[i]
        if point > SMhigh:  # center about zero
            total += point - SMhigh
        elif point < SMlow:
            total += point - SMlow
        else:
            total += 0  # only add outliers
    return total

@DeprecationWarning
def first_detected(data, thresholds, start=0):
    for i, v in enumerate(data[start:]):
        if v > thresholds[1]:
            return i + start
    if start >= len(data):
        return start
    return i + start


def calculate_t(RUCns, RUCps, w1):
    w2 = 1 - w1
    losses_plus = []
    losses_minus = []

    n = len(RUCps)
    # calculate positive bound
    if n > 0:
        for 𝜏 in np.linspace(min(RUCps), max(RUCps), 500):
            cost = 0
            penalty = 0
            for r in RUCps:
                if r > 𝜏:
                    cost += w1 * abs(r - 𝜏)
                else:
                    penalty += w2 * abs(r - 𝜏)
            losses_plus.append((cost + penalty) / n)

    n = len(RUCns)
    # calculate negative bound
    if n > 0:
        for 𝜏 in np.linspace(min(RUCns), max(RUCns), 500):
            cost = 0
            penalty = 0
            for r in RUCns:
                if r < 𝜏:
                    cost += w1 * abs(r - 𝜏)
                else:
                    penalty += w2 * abs(r - 𝜏)
            losses_minus.append((cost + penalty) / n)
    tp = 0 if len(RUCps) == 0 else np.linspace(min(RUCps), max(RUCps), 500)[np.argmin(losses_plus)]
    tn = 0 if len(RUCns) == 0 else np.linspace(min(RUCns), max(RUCns), 500)[np.argmin(losses_minus)]
    return (tn, tp)


@calc_cache
def calculate_data(file, e:float=2.7, l:int =50, fl:int = 9, w1:float=0.1, simple:bool = False, *args, **kwargs):
    # get differences in times and direct data from file
    timediffs, attack, x0 = read(file)

    # calculate ratios and RUCs
    ratios_of = lambda data: [R(data[i:j]) for i,j in window(0, len(timediffs), l, include_extra=False)]
    ratios = ratios_of(timediffs)

    mean = avg(ratios)
    std_dev = math.sqrt(sum([(x-mean)**2 for x in ratios])/(len(ratios)-1))

    SMhigh = mean + e * std_dev
    SMlow = mean - e * std_dev

    RUCs = [RUC(ratios, SMlow, SMhigh, T, fl) for T in range(len(ratios))]


    # thresholds for RUCs (algorithm 1)
    thresholds = calculate_t([x for x in RUCs if x < 0], [x for x in RUCs if x > 0], w1=w1)
    print("thresholds =", thresholds)


    windowed_detections = [] # calculating values based on RUC values, not absolute by attack
    for i, j in window(0, len(attack), l, include_extra=False):
        windowed_detections.append(1 in attack[i:j])

    first_attack = windowed_detections.index(True)
    try:
        time_to_detection = [x > thresholds[1] for x in RUCs].index(True) - first_attack
    except ValueError:
        time_to_detection = len(windowed_detections) # didnt find any attacks

    false_alarm = missed = 0
    for i in range(len(windowed_detections)):
        if windowed_detections[i] == False and RUCs[i] > thresholds[1]:
            false_alarm += 1
        if windowed_detections[i] == True and RUCs[i] <= thresholds[1]:
            missed += 1

    # print(f"{first_attack=}")
    # print(f"{time_to_detection=}")
    # print(f"{false_alarm=}")
    # print(f"{missed=}")



    #  the most important is the false alarm count, time to detection, and last the missed detection rate.
    toReturn = {"ttd": time_to_detection,
                "fa": false_alarm,
                'md': missed
                }
    print(toReturn)
    if not simple: # if simple, do not cache
        toReturn.update({
            'SMlow':SMlow,
            'SMhigh':SMhigh,
            'mean':mean,
            'ratio':ratios,
            'std_dev':std_dev,
            'timediffs': timediffs,
            'thresholds': thresholds,
            'RUCs':RUCs
            })
    return toReturn
