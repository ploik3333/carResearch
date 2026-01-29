import numpy as np

from utila import *

#useful simple functions
safediv = lambda a: 0 if a == 0 else 1/a # no divide by zero, 1/0 is 0 here
harmonic = lambda a: len(a) * safediv(sum(map(safediv, a)))
arithmetic = avg = lambda a: np.asarray(a).mean() # sum(a)/len(a)
# R = lambda x: harmonic(x) * safediv(arithmetic(x))
# R = lambda x: len(x)**2 / sum(x) / sum(map(safediv, x))
def R(x): # used math and numpy to speed up significantly
    x = np.asarray(x)
    inv_s = np.reciprocal(x, where=x!=0, out=None).sum()
    return x.size*x.size / (x.sum() * inv_s)


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
    _, RUCs, _, _= calc_RUCs(timediffs, e, l, fl)
    if len(RUCs[RUCs < 0]) < 1:
        tn = 0
    else:
        tn = np.nanquantile(RUCs[RUCs < 0], w1)   #[x for x in RUCs if x < 0], w1)
    if len(RUCs[RUCs > 0]) < 1:
        tp = 0
    else:
        tp = np.nanquantile(RUCs[RUCs > 0], w1)   #[x for x in RUCs if x > 0], w1)
    if np.isnan(tn):
        tn = 0
    if np.isnan(tp):
        tp = 0

    return tn, tp

def calc_RUCs(timediffs, e, l, fl):
    # calculate ratios and RUCs
    #uses cool numpy array logic rather than the R() function used before, but equivilent
    cumsum = np.concatenate(([0.0], np.cumsum(timediffs)))
    invcumsum = np.concatenate(([0.0], np.cumsum(np.reciprocal(timediffs, where=timediffs != 0, out=None))))
    i = np.arange(0, timediffs.size-l+1, l)

    ratios = l*l / ((cumsum[i+l]-cumsum[i]) * (invcumsum[i+l] - invcumsum[i]))
    #does the same, just much slower
    # ratios = [R(timediffs[i:j]) for i, j in window( len(timediffs), l, include_extra=False)])

    mean = ratios.mean()
    std_dev = math.sqrt(((ratios-mean) ** 2).sum() / (len(ratios) -1))
    SMhigh = mean + e * std_dev
    SMlow = mean - e * std_dev


    RUCs = np.asarray([RUC(ratios, SMlow, SMhigh, T, fl) for T in range(len(ratios))])
    return ratios, RUCs, SMlow, SMhigh

@cache
def evaluate(file, benign, e:float=2.7, w1:float=0.1, l:int =50, fl:int = 9, simple:bool = True, verbose:bool = False, *args, **kwargs):
    e = float(e)
    w1 = float(w1)
    fl = int(fl)
    l = int(l)

    timediffs, attack, x0 = read(file)
    ratios, RUCs, SMlow, SMhigh = calc_RUCs(timediffs, e, l, fl)


    # algorithm 1 with tao # get these from benign datasets
    tn, tp = benign_calculations(benign, e = e, w1 = w1, fl = fl, l = l)

    windowed_detections = []  # calculating values based on RUC values, not absolute by attack
    for i, j in window(0, len(timediffs), l, include_extra=False):
        windowed_detections.append(1 in attack[i:j])
    if verbose:
        print(f"e={e:.2f}, w1={w1:.2f}, fl={fl}, l={l}")
        print(len(windowed_detections), len(RUCs), attack.size)
        print("tn:", repr(tn),"tp:", repr(tp))
        print("detected attacks:", sum([x > tp or x < tn for x in RUCs]))
        print("window attacks:", windowed_detections.count(True))
        print("missed attacks:", sum([tn <= x <= tp for i,x in enumerate(RUCs) if windowed_detections[i] ]))

    try:
        first_attack = windowed_detections.index(True)
    except ValueError:
        first_attack = len(RUCs)
    for i, frame in enumerate(RUCs):
        if frame > tp:  # above threshold => detected attack
            time_to_detection = max(0, i-first_attack)
            break
    else:  # didnt find one
        time_to_detection = len(windowed_detections)

    false_alarm = missed = 0 # initialize
    for i in range(len(windowed_detections)): # count fa and md as loop
        if windowed_detections[i] == False and RUCs[i] > tp or RUCs[i] < tn:
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
            'attacks': attack,
            'thresholds': (tn, tp),
            'RUCs':RUCs
            })
    return toReturn


def compare(e,f):
    a_win = 0
    a = getFiles('./data/attack')
    b = getFiles('./data/benign')
    tfd = lambda di: (di['fa'], di['ttd'], di['md'])
    for c in range(len(a)):
        for d in range(c+1, len(b)):
            if tfd(evaluate(a[c],b[d], *e)) < tfd(evaluate(a[c],b[d], *f)):
                a_win+=1
            if a_win  > len(a)*len(b) / 2:
                return True
            if len(a)*len(b) / 2 - a_win < len(a)*len(b)-(c*len(b)+d):
                return False
    return a_win >= (len(a) * len(b)) / 2