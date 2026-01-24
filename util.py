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


def benign_calculations(file, e,w1,fl,l):
    timediffs, _, _ = read(file)
    ratios, RUCs, _, _= calc_RUCs(timediffs, e, l, fl)

    tn = np.nanquantile([x for x in RUCs if x < 0], w1)
    tp = np.nanquantile([x for x in RUCs if x > 0], w1)
    if tn == np.nan:
        tn = 0
    if tp == np.nan:
        tp = 0

    return tn, tp



def calc_RUCs(timediffs, e, l, fl):
    # calculate ratios and RUCs
    ratios_of = lambda data: [R(data[i:j]) for i, j in window(0, len(timediffs), l, include_extra=False)]
    ratios = ratios_of(timediffs)

    mean = avg(ratios)
    std_dev = math.sqrt(sum([(x - mean) ** 2 for x in ratios]) / (len(ratios) - 1))

    SMhigh = mean + e * std_dev
    SMlow = mean - e * std_dev

    # 0.07 seconds, fine
    RUCs = [RUC(ratios, SMlow, SMhigh, T, fl) for T in range(len(ratios))]
    return ratios, RUCs, SMlow, SMhigh

@cache
def evaluate(file_i, e:float=2.7, l:int =50, fl:int = 9, w1:float=0.1, simple:bool = True, *args, **kwargs):
    file = Path(f'./data/attack/Dos-{file_i}-a.csv')
    timediffs, attack, x0 = read(file)
    ratios, RUCs, SMlow, SMhigh = calc_RUCs(timediffs, e, l, fl)


    # algorithm 1 with tao # get these from benign datasets
    tn, tp = benign_calculations(Path(f'./data/benign/Dos-{file_i}-p.csv'), e = e, w1 = w1, fl = fl, l = l)

    windowed_detections = []  # calculating values based on RUC values, not absolute by attack
    for i, j in window(0, len(attack), l, include_extra=False):
        windowed_detections.append(1 in attack[i:j])

    try:
        first_attack = windowed_detections.index(True)
    except ValueError:
        first_attack = len(RUCs)
    for i, frame in enumerate(RUCs):
        if frame > tp:  # above threshold => detected attack
            time_to_detection = i
            break
    else:  # didnt find one
        time_to_detection = len(windowed_detections)

    false_alarm = missed = 0 # initialize
    for i in range(len(windowed_detections)): # count fa and md as loop
        if windowed_detections[i] == False and (RUCs[i] > tp or RUCs[i] < tn):
            false_alarm += 1
        if windowed_detections[i] == True and (tn <= RUCs[i] <= tp):
            missed += 1

    #  the most important is the false alarm count, time to detection, and last the missed detection rate.
    toReturn = {
        "ttd": time_to_detection*l, # multiply by l to get ~total frames - not biased to large values of l
        "fa": false_alarm,
        'md': missed / windowed_detections.count(True)
                }


    if not simple: # if simple, do not return (long, dont unnecessarily return)
        toReturn.update({
            'SMlow':SMlow,
            'SMhigh':SMhigh,
            # 'mean':mean,
            'ratio':ratios,
            # 'std_dev':std_dev,
            'timediffs': timediffs,
            'thresholds': (tn, tp),
            'RUCs':RUCs
            })
    return toReturn
