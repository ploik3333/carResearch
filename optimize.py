import random
from pathlib import Path

from deap import base, creator, tools, algorithms

from util import calculate_data

last = [[], []]


def get(e, fl, l, w1, p):  # simlpe cache only for last call
    global last
    if last[0] == [e, fl, l, w1]:
        if last[1] is None:
            return
        return last[1][p]
    file = Path("./data/attack") / "DoS-3-a.csv"
    last = [[e, fl, l, w1], calculate_data(file, e=e, w1=w1, fl=fl, l=l, cache=False, simple=True)]
    if last[1] is None:
        return
    return last[1][p]


# get values from calculate function
def evaluate(individual, eps_ttd, eps_md):
    e, w1, fl, l = individual
    fa = get(e=e, fl=fl, l=l, w1=w1, p='fa')
    ttd = get(e=e, fl=fl, l=l, w1=w1, p='ttd')
    md = get(e=e, fl=fl, l=l, w1=w1, p='md')

    if not (ttd <= eps_ttd) and (md <= eps_md):
        return (1e10,)
    return (fa,)


# using genetic algorithm, so
def custom_mutation(individual, indpb):
    if random.random() < indpb:
        e, w1, fl, l = individual
        e += random.gauss(0, 1)
        w1 += random.gauss(0, 1)
        fl += random.randint(-2, 2)
        fl = max(2, fl)
        l += random.randint(-2, 2)
        l = max(2, l)

        individual[:] = [e, w1, fl, l]

    return (individual,)


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # Minimize false alarm
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()

# create limits for data
toolbox.register("e", random.uniform, 0, 5)  # assume e will not be above 5
toolbox.register("w1", random.uniform, 0, 1)  # w1 is limited by definition to this range
toolbox.register("fl", random.randint, 2, 200)  # assume an upper limit for window ranges
toolbox.register("l", random.randint, 2, 200)  # and cant be 1

# create the data types in the way defined in calculate_data function
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.e, toolbox.w1, toolbox.fl, toolbox.l), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxTwoPoint)  # recomended values for mixed integer programming
toolbox.register("mutate", custom_mutation, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

toolbox.register("evaluate", evaluate, eps_ttd=0, eps_md=0)

pop = toolbox.population(n=100)
hof = tools.HallOfFame(1)

algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=50,
                    halloffame=hof, verbose=False)

best = hof[0]
results = simulate_system(*best)

[e, w1, fl, l] = best

print(f"Optimal Inputs: e={best_vars[0]:.2f}, w1={best_vars[1]:.2f}, fl={best_vars[2]}, l={best_vars[3]}")
print(f"Results -> fa: {results[0]:.2f} (minimized), ttd: {results[1]:.2f}, md: {results[2]:.2f}")

# Results from one trial (Takes forever)
# Optimal Inputs: e=4.66, w1=0.82, fl=111, l=152
# Results -> fa: 61.00 (minimized), ttd: 125.43, md: 0.00
