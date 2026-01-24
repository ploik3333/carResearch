import random
from pathlib import Path

from deap import base, creator, tools, algorithms

import util
import utila


# get values from util.evaluate
def evaluate(individual):
    e, w1, fl, l = individual
    file = 3#Path("./data/attack") / "DoS-3-a.csv"
    results = util.evaluate(file, e=e, w1=w1, fl=fl, l=l)

    fa = results['fa']
    ttd = results['ttd']
    md = results['md']

    # if not ((ttd <= 0.5) and (md <= 0.55)): # listed in the paper as the constraints
    #     return (1e10,1e10,1e10) # big number means it doesnt work
    print([e, w1, fl, l], [fa,ttd, md])
    return (fa,ttd, md) # added other two


# using genetic algorithm, so
def custom_mutation(individual, indpb):
    if random.random() < indpb: # add a small amount to each value to simulate 'mutation'
        e, w1, fl, l = individual
        e += random.gauss(0, 1)
        e = max(0, e)
        w1 += random.gauss(0, 1)
        w1 = max(0, min(1, w1))
        fl += random.randint(-2, 2)
        fl = max(2, fl)
        l += random.randint(-2, 2)
        l = max(2, l)

        individual[:] = [e, w1, fl, l] #dont want to redefine if no change


    return (individual,)


creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0,-1.0))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()
history = tools.History()

# create limits for data
toolbox.register("e", random.uniform, 0, 5)  # assume e will not be above 5
toolbox.register("w1", random.uniform, 0, 1)  # w1 is limited by definition to this range
toolbox.register("fl", random.randint, 2, 200)  # assume an upper limit for window ranges
toolbox.register("l", random.randint, 2, 200)  # and cant be 1

# create the data types in the way defined in util.evaluate function
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.e, toolbox.w1, toolbox.fl, toolbox.l), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxTwoPoint)  # recomended values for mixed integer programming
toolbox.register("mutate", custom_mutation, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

toolbox.register("evaluate", evaluate)

pop = toolbox.population(n=100)
hof = tools.HallOfFame(1)

# calls evaluate and mutate for us, makes it easier
utila.discord_log("STARTING OPTIMIZATION")
algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=50, halloffame=hof, verbose=True)
utila.discord_log("DONE WITH OPTIMIZATION")

[e, w1, fl, l] = hof[0] # lexicographical sorting, as variables are ordered by imporetance, it gets the least of each
results = util.evaluate(3, e=e, w1=w1, fl=fl, l=l)


print(f"{'Best Found Results':^30}")
print(f"e={e:.2f}, w1={w1:.2f}, fl={fl}, l={l}")
print(f"fa: {results['fa']:.2f}, ttd: {results['ttd']:.2f}, md: {results['md']:.2f}")


