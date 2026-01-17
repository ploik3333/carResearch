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

"""
...
# from pymoo.algorithms.soo.nonconvex.de import DE
# from pymoo.constraints.eps import AdaptiveEpsilonConstraintHandling
# from pymoo.optimize import minimize
# from pymoo.problems.single import G1
# from pymoo.core.problem import ElementwiseProblem
#
# class ConstrainedProblemWithEquality(ElementwiseProblem):
#
#     def __init__(self, **kwargs):
#         super().__init__(n_var=2, n_obj=1, n_ieq_constr=1, n_eq_constr=1, xl=0, xu=1, **kwargs)
#
#     def _evaluate(self, x, y, out, *args, **kwargs):
#         out["F"] = x[0] + x[1] + math.sin(y)
#         out["G"] = 1.0 - (x[0] + x[1]) + math.cos(y)
#         out["H"] = 3 * x[0] - x[1]
#
# problem = ConstrainedProblemWithEquality()
#
# algorithm = AdaptiveEpsilonConstraintHandling(DE(), perc_eps_until=0.5)
#
# res = minimize(problem,
#                algorithm,
#                ('n_gen', 200),
#                seed=1,
#                verbose=False)
#
# print("Best solution found: \nX = %s\nF = %s\nCV = %s" % (res.X, res.F, res.CV))
#
#
...
# import openmdao.api as om
# import numpy as np
#
# # build the model
# prob = om.Problem()
#
# prob.model.add_subsystem('paraboloid_1', om.ExecComp('g = (x-3)**2'), promotes=['*'])
# prob.model.add_subsystem('paraboloid_2', om.ExecComp('h = (x+1)**2 + 3*x'), promotes=['*'])
# prob.model.add_subsystem('objective', om.ExecComp('f = alpha * g + beta * h'), promotes=['*'])
#
# # setup the optimization
# prob.driver = om.ScipyOptimizeDriver()
# prob.driver.options['optimizer'] = 'SLSQP'
#
# prob.model.add_design_var('x', lower=-50, upper=50)
# prob.model.add_objective('f')
#
# prob.setup()
#
# # Set initial values.
# prob.set_val('x', 3.0)
# prob.set_val('alpha', 0.5)  # Vary these values to see different trends
# prob.set_val('beta', 0.5)
#
# # run the optimization
# prob.run_driver();
#
# print(prob['x'], prob['f'])
...
# with open("find-3.txt", "w") as fout:
#     timediffs = []
#     with open("DoS-3.csv", "r") as fin:
#         timestamp, arbitration_id, data_field = fin.readline().split(",")  # ignore headers
#         raw = fin.read().strip().split("\n")
#         data = list(map(process_data, raw))  # use process_data function for each line, to extract values
#
#         # calculate time differences
#         # lasttime = data[0][0]
#         # for line in data:
#         #     timestamp, arbitration_id, data_field = line
#         #     timediffs.append(timestamp - lasttime)
#         #     lasttime = timestamp
#         timediffs = [data[i][0]-data[i+1][0] for i in range(len(data)-1)]
#
#     fout.write(",".join([timestamp, arbitration_id, data_field] )+ "\n")
#     fout.write("\n".join([f"{i},{raw[i]},{timediffs[i]}" for i in range(len(raw)-1)]))
...
# complicaded e for proj

# x_values_constrained = []
# g_values_constrained = []
# h_values_constrained = []
#
# g_constraints = np.linspace(0., 30., 21)
# om.ExecComp.register("domath", lambda x:x**2, complex_safe=True)
#
#
# for g_const in g_constraints:
#     # build the model
#     prob = om.Problem(work_dir = "./data/om")
#
#     prob.model.add_subsystem('a', om.ExecComp('g = x**2'), promotes=['*'])
#     prob.model.add_subsystem('b', om.ExecComp('h = sin(x)'), promotes=['*'])
#
#     # setup the optimization
#     prob.driver = om.ScipyOptimizeDriver()
#     prob.driver.options['optimizer'] = 'SLSQP'
#
#     prob.model.add_design_var('x', lower=-50, upper=50)
#     prob.model.add_constraint('g', equals=g_const)
#     prob.model.add_objective('h')
#
#     prob.setup(check=False)
#
#     # run the optimization
#     prob.run_driver()
#
#     x_values_constrained.append(float(prob["x"][0]))
#     g_values_constrained.append(float(prob["g"][0]))
#     h_values_constrained.append(float(prob["h"][0]))
#
# plt.plot(g_values_constrained, h_values_constrained, marker='o')
# plt.xlabel('g(x)')
# plt.ylabel('h(x)')
#
# print(x_values_constrained, g_values_constrained, h_values_constrained, sep="\n")
# plt.show()
...
# basic
# We'll use the component that was defined in the last tutorial
# from openmdao.test_suite.components.paraboloid import Paraboloid
# import openmdao.api as om
# fig, axes = plt.subplots(nrows=max(1, len(csv_files)), ncols=2, layout="constrained")
...

#  the most important is the false alarm count, time to detection, and last the missed detection rate.
...
# OPTIONS FOR OPENMDAO
# om.ExecComp.register("func", lambda x:(x+2)**2-6, complex_safe=True)
# prob.model.add_constraint('const.g', lower=0, upper=10.)
# prob.model.add_design_var('x', lower=-50, upper=50)
# prob.model.add_objective('const.g')
# prob.model.add_subsystem('const', om.ExecComp('g = a(x) '), promotes_inputs=['x'])
# prob.model.set_input_defaults('y', -4.0)




# build the model
# prob = om.Problem()
# om.ExecComp.register("a", lambda x:(x+2)**2-6, complex_safe=True)
# # prob.model.add_subsystem('parab', om.ExecComp('f = 2x+3'), promotes_inputs=['x'])
#
# # define the component whose output will be constrained
# prob.model.add_subsystem('const', om.ExecComp('g = a(x)+cos(y) '), promotes_inputs=['x','y'])
# prob.model.add_subsystem('asdf', om.ExecComp('g = sin(y)-2*cos(y/2) '), promotes_inputs=['y'])
#
# prob.model.set_input_defaults('x', 3.0)
# # prob.model.set_input_defaults('y', -4.0)
#
#
# prob.model.add_design_var('x', lower=-50, upper=50)
# prob.model.add_design_var('y', lower=-50, upper=50)
# prob.model.add_objective('const.g')
# prob.model.add_constraint('asdf.g', lower=1, upper=10.)
#
# # setup model to run
# prob.driver = om.ScipyOptimizeDriver()
# prob.driver.options['optimizer'] = 'SLSQP'
# prob.setup()
# prob.run_driver()
#
# print(prob.get_val('const.x')[0])
#
# # om.n2(prob)
...
# 3D PLOT THE THING
# ax = plt.figure().add_subplot(projection='3d')
# # X, Y, Z = axes3d.get_test_data(0.05)
# x = np.linspace(-50, 50, 500)
# y = np.linspace(-50, 50, 500)
# X, Y = np.meshgrid(x, y)
# Z = np.zeros_like(X)
#
# for i in range(len(x)):
#     for j in range(len(y)):
#         prob.set_val('const.x', X[i, j])
#         prob.set_val('asdf.y', Y[i, j])
#         prob.run_model()
#         Z[i, j] = prob.get_val('const.g')
#
#
# plt.contourf(X, Y, Z, levels=50)
# plt.colorbar(label='Objective Value')
# plt.xlabel('Variable X')
# plt.ylabel('Variable Y')
# plt.show()


# hyperparameters
...
# prob = om.Problem(work_dir = "./cache/om")

# om.ExecComp.register("func", lambda x:calculate_data, complex_safe=True)

# prob.model.add_objective()

# TODO: remove these
# its either now, or after a breakdown in 8 years
# there is still time
# oh no the mental health has infected code too
# also yes i just watched I saw the TV glow, thanks for asking
# r = calculate_data(Path(".")/"data/benign/DoS-1-p.csv", simple = True, benign = True, cache = True)
# for x in r:
#     print(f"{x}: {r[x]}")
...
# r = calculate_data(Path(".")/"data/benign/DoS-1-p.csv", w1 = 0.9, benign = True, cache = True)
# import matplotlib.pyplot as plt
# x = range(1, len(r['RUCs']) + 1)
# plt.scatter(x, r['RUCs'], s=1)
# print(r['thresholds'])
# plt.plot(x, [r['thresholds'][0] for _ in x], color="green")
# plt.plot(x, [r['thresholds'][1] for _ in x], color="green")
# plt.show()
...
# fig, axes = plt.subplots(nrows=4, ncols=2, layout="constrained")
# for i in range(1,5):
#     datadict = calculate_data(f'./data/benign/DoS-{i}-p.csv', benign = True)
#     axes[i-1][0].scatter(range(1, len(datadict['RUCs']) + 1), datadict['RUCs'], s=1)
#     datadict = calculate_data(f'./data/attack/DoS-{i}-a.csv', benign = False)
#     axes[i-1][1].scatter(range(1, len(datadict['RUCs']) + 1), datadict['RUCs'], s=1)
# plt.show()
"""


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