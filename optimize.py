import random
from pathlib import Path

from deap import base, creator, tools, algorithms

import util
import utila

class rand_file:
    def __init__(self, max):
        self.max = max
        self.last = None

    def __index__(self):
        self.last = random.randint(0, self.max)
        # print(f"getting file {self.last}")
        return self.last

    def get_last(self):
        return self.last
FILE_INDEX = rand_file(len(util.getFiles('./data/attack')) - 1)


def deap_optimizer():
    # get values from util.evaluate
    def evaluate(individual):
        e, w1, fl, l = individual
        file = util.getFiles('./data/attack')[FILE_INDEX]
        benign = util.getFiles('./data/benign')[FILE_INDEX.get_last()]
        results = util.evaluate(file, benign, e=e, w1=w1, fl=fl, l=l)

        fa = results['fa']
        ttd = results['ttd']
        md = results['md']

        # if not ((ttd <= 0.5) and (md <= 0.55)): # listed in the paper as the constraints
        #     return (1e10,1e10,1e10) # big number means it doesnt work
        print([e, w1, fl, l], [fa, ttd, md])
        return (fa, ttd, md)  # added other two

    # using genetic algorithm, so
    def custom_mutation(individual, indpb):
        e, w1, fl, l = individual
        if random.random() < indpb:  # add a small amount to each value to simulate 'mutation'
            e += random.gauss(0, 1)
            e = max(0, e)
        if random.random() < indpb:
            w1 += random.gauss(0, 1)
            w1 = max(0, min(1, w1))
        if random.random() < indpb:
            fl += random.randint(-2, 2)
            fl = max(2, fl)
        if random.random() < indpb:
            l += random.randint(-2, 2)
            l = max(2, l)

        individual[:] = [e, w1, fl, l]  # dont want to redefine, just update

        return (individual,)

    creator.create("FitnessMin", base.Fitness, weights=(-10000.0, -1.0, -0.00001))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    toolbox = base.Toolbox()
    history = tools.History()

    # create limits for data
    toolbox.register("e", random.uniform, 0, 5)
    toolbox.register("w1", random.uniform, 0, 1)
    toolbox.register("fl", random.randint, 2, 200)
    toolbox.register("l", random.randint, 2, 200)

    # create the data types in the way defined in util.evaluate function
    toolbox.register("individual", tools.initCycle, creator.Individual,
                     (toolbox.e, toolbox.w1, toolbox.fl, toolbox.l), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mate", tools.cxTwoPoint)  # recomended values for mixed integer programming
    toolbox.register("mutate", custom_mutation, indpb=0.3)
    toolbox.register("select", tools.selTournament, tournsize=3)

    toolbox.register("evaluate", evaluate)

    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)

    class rand_file:
        def __init__(self, max):
            self.max = max
            self.last = None
        def __index__(self):
            self.last = random.randint(0, self.max)
            print(f"getting file {self.last}")
            return self.last
        def get_last(self):
            return self.last
    FILE_INDEX = rand_file(len(util.getFiles('./data/attack'))-1)
    # calls evaluate and mutate for us, makes it easier
    algorithms.eaSimple(pop, toolbox, cxpb=0.65, mutpb=0.4, ngen=100, halloffame=hof, verbose=True)
    utila.discord_log("DONE WITH OPTIMIZATION")

    [e, w1, fl, l] = hof[0] # lexicographical sorting, as variables are ordered by imporetance, it gets the least of each


    file = util.getFiles('./data/attack')[FILE_INDEX]
    benign = util.getFiles('./data/benign')[FILE_INDEX.get_last()]
    results = util.evaluate(file, benign, e=e, w1=w1, fl=fl, l=l)


    print(f"{'Best Found Results':^30}")
    print(f"e={e:.2f}, w1={w1:.2f}, fl={fl}, l={l}")
    print(f"fa: {results['fa']:.2f}, ttd: {results['ttd']:.2f}, md: {results['md']:.2f}")

def skopt_optimizer():
    def evaluate_cached(e, w1, fl, l):
        file = util.getFiles('./data/attack')[FILE_INDEX]
        benign = util.getFiles('./data/benign')[FILE_INDEX.get_last()]
        return util.evaluate(file, benign, float(e), float(w1), int(fl), int(l))

    from skopt.space import Real, Integer
    from skopt import gp_minimize

    space = [
        Real(0.0, 5.0, name="e"),
        Real(0.0, 1.0, name="w1"),
        Integer(2, 200, name="fl"),
        Integer(2, 200, name="l"),
    ]


    def obj_fa(x):
        e, w1, fl, l = x
        return evaluate_cached(e, w1, fl, l)["fa"]

    res_fa = gp_minimize(
        obj_fa,
        space,
        n_calls=400,
        n_initial_points=10,
        acq_func="EI",
        random_state=0,
    )

    best_fa = res_fa.fun
    print("BEST FA:", best_fa , "WITH:", "e={}, w1={}, fl={}, l={}".format(*res_fa.x))
    EPS_FA = 1e-6

    def obj_ttd(x):
        e, w1, fl, l = x
        out = evaluate_cached(e, w1, fl, l)

        if out["fa"] > best_fa + EPS_FA:
            return 1e9  # infeasible

        return out["ttd"]


    res_ttd = gp_minimize(
        obj_ttd,
        space,
        n_calls=400,
        n_initial_points=10,
        acq_func="EI",
        random_state=1,
    )

    best_ttd = res_ttd.fun
    print("BEST TTD:", best_ttd , "WITH:", "e={}, w1={}, fl={}, l={}".format(*res_ttd.x))

    EPS_TTD = 1e-6

    def obj_md(x):
        e, w1, fl, l = x
        out = evaluate_cached(e, w1, fl, l)

        if out["fa"] > best_fa + EPS_FA:
            return 1e9
        if out["ttd"] > best_ttd + EPS_TTD:
            return 1e9

        return out["md"]

    res_md = gp_minimize(
        obj_md,
        space,
        n_calls=400,
        n_initial_points=10,
        acq_func="EI",
        random_state=2,
    )

    x_star = res_md.x
    final_vals = evaluate_cached(*x_star)
    print("BEST TOTAL:", "fa={}, ttd={}, md={}".format(*final_vals) , "\nWITH:", "e={}, w1={}, fl={}, l={}".format(*x_star))


    fl_star, l_star = x_star[2], x_star[3]
    def local_obj(x):
        e, w1 = x
        out = evaluate_cached(e, w1, fl_star, l_star)
        return (
            out["fa"] * 1e12 +
            out["ttd"] * 1e6 +
            out["md"]
        )

    res_final = gp_minimize(
        local_obj,
        [
            Real(0.0, 5.0, name="e"),
            Real(0.0, 1.0, name="w1")
            ],
        n_calls=400,
        n_initial_points=10,
        acq_func="EI",
        random_state=2,
    )

    final_vals = evaluate_cached(*res_final.x, fl_star, l_star)
    print("BEST TOTAL:", "fa={}, ttd={}, md={}".format(*final_vals) , "\nWITH:", "e={}, w1={}, fl={}, l={}".format(*res_final.x, fl_star, l_star))




def evaluate_cached(e, w1, fl, l):
    file = util.getFiles('./data/attack')[FILE_INDEX]
    benign = util.getFiles('./data/benign')[FILE_INDEX.get_last()]
    results = util.evaluate(file, benign, float(e), float(w1), int(fl), int(l))
    return results['fa'], results['ttd'], results['md']
def custom_mutation(e, w1, fl, l, indpb):
    if random.random() < indpb:  # add a small amount to each value to simulate 'mutation'
        e += random.gauss(0, 1)
        e = max(0, e)
    if random.random() < indpb:
        w1 += random.gauss(0, 1)/3 # change less
        w1 = max(0, min(1, w1))
    if random.random() < indpb:
        fl += random.randint(-2, 2)
        fl = max(2, fl)
    if random.random() < indpb:
        l += random.randint(-2, 2)
        l = max(2, l)

    return e, w1, fl, l


g_best = (random.random()*4, random.random(), random.randint(2,100), random.randint(2,100))
g_eval_best = evaluate_cached(*g_best)
# print(g_best, g_eval_best)
for trial in range(10):
    best_ = (random.random() * 4, random.random(), random.randint(2, 100), random.randint(2, 100))
    eval_best_ = evaluate_cached(*best_)
    # print(best_, eval_best_)
    for _ in range(2000):
        new = custom_mutation(*best_, indpb=0.2)
        # print("BEST:", new)
        eval_new = evaluate_cached(*new)
        # print(new, eval_new)
        if eval_new < eval_best_: #util.compare(eval_new, eval_best_):
            best_ = new
            eval_best_ = eval_new
        if eval_new < g_eval_best: #util.compare(eval_new, eval_best_):
            g_best = new
            g_eval_best = eval_new
    print(f"done with trial {trial}")


print("BEST TOTAL:", "fa={}, ttd={}, md={}".format(*g_eval_best) , "\nWITH:", "e={}, w1={}, fl={}, l={}".format(*g_best))
