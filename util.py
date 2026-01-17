import numpy as np

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
def calculate_data(file, e:float=2.7, l:int =50, fl:int = 9, w1:float=0.1, benign:bool = False, simple:bool = False, *args, **kwargs):
    fl = int(fl)
    l = int(l)


    # get differences in times and direct data from file
    timediffs, attack, x0 = read(file)
    if attack and sum(attack) == 0: benign = True
    if benign: attack = None



    # calculate and display ratios
    print(l)
    assert type(l) == int
    ratios_of = lambda data: [R(data[i:j]) for i,j in window(0, len(timediffs), l, include_extra=False)]
    ratios = ratios_of(timediffs)
    # print(ratios[:10])

    mean = avg(ratios)
    std_dev = math.sqrt(sum([(x-mean)**2 for x in ratios])/(len(ratios)-1))
    print(f"{std_dev = }")

    SMhigh = mean + e * std_dev
    SMlow = mean - e * std_dev
    print(f"{SMhigh = }")
    print(f"{SMlow = }")



    RUCs = [RUC(ratios, SMlow, SMhigh, T, fl) for T in range(len(ratios))]
    if benign:
        thresholds = calculate_t([x for x in RUCs if x < 0], [x for x in RUCs if x > 0], w1=w1)
        print("threshold =", thresholds[1])
    else:
        thresholds = (0,0)

    if attack:
        first_attack = attack.index(1)
        print(f"{first_attack = }")
        print("FIRST DETECTED window =", first_detected(RUCs, thresholds, start=first_attack//l))
        time_to_detection = x0[first_detected(RUCs, thresholds, start=first_attack//l) * l] - x0[0]


        false_alarm = sum([v > thresholds[1] for i,v in enumerate(RUCs) if attack[i] == 0])
        missed = sum([v <= thresholds[1] for i,v in enumerate(RUCs) if attack[i] == 1])

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
    toReturn = {"ttd": time_to_detection,
                "fa": false_alarm,
                'md': missed
                }
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
