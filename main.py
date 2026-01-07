from typing import Tuple, Generator, Any, overload
import math
import scipy
import matplotlib.pyplot as plt
import os
from pathlib import Path
# from pypdf import PdfReader
# import fitz
# import fontTools
# from scipy.optimize import minimize
import numpy as np
import openmdao.api as om
from util import *
from mpl_toolkits.mplot3d import axes3d







# stufff i havent gotten rid of yet, skip to like 92
"""
# plot one dataset, and average Y
# timediffs, data = read("DoS-1.csv")
# x =  list(map(lambda x:float(x[0]), data))
# y = timediffs
# avgy = sum(timediffs)/len(timediffs)
#
# x2, y2 = avgout(x, y)
# y2 = [avgy - a for a in y2]
#
# fig, axes = plt.subplots(nrows=3)
# fig.suptitle('Data')
# plt.subplots_adjust(hspace=.6)
# axes[0].plot(x, y)
# axes[0].plot(x, [avgy for _ in x])
# axes[0].set_title("Data")
# axes[1].plot(x2, y2)
# axes[1].set_title("Residuals")
# window2 = [*window(len(x), 10000)][:-2]
# axes[2].plot(list(x[a] for a,_ in window2), [*map(avg, [timediffs[i:j] for i,j in window2])])
# print(window2)
# print(list(x[a] for a,_ in window2), [*map(avg, [timediffs[i:j] for i,j in window2])], sep="\n\n")
# axes[2].set_title("Average over range")
#
#
#
# plt.show()
"""


# find all csv files, so doesnt have to be hard-coded
csv_files: list[Path] = [Path('./data/') / Path(file) for file in os.listdir("./data") if Path(file).suffix == ".csv"]
# csv_files = []
HARD_CODED_STARTS = {"DoS-1.csv": 18076, "DoS-2.csv": 44728, "DoS-3.csv": 44728, "DoS-4.csv": 44728} # (?<!772|17F),0{16}
# print([file for file in os.listdir("./data") if Path(file).suffix == ".csv"])

# using matplotlib
fig, axes = plt.subplots(nrows=max(1, len(csv_files)), ncols=4, layout="constrained")



i: int = 0

# loop through all csv files / Main Loop
for file in csv_files:
    # print(f"calculating {file}")
    datadict = calculate_data(file, e = 2.7)
    # print(datadict)

    axes[i][0].set_title(file)
    axes[i][1].set_title("Ratios of avgs")
    axes[i][2].set_title("'RUC's (sum outliers)")


    # plot length of time between each ecu broadcast
    axes[i][0].plot(range(1, len(datadict['timediffs'])+1), datadict["timediffs"])
    # plot ratios
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), datadict['ratio'])
    # plot RUC
    axes[i][2].plot(range(1, len(datadict['RUCs']) + 1), datadict['RUCs'])
    # plot ratio of RUCs
    axes[i][3].plot(range(1, len(datadict['RRUCs']) + 1), datadict['RRUCs'])


    # plot upper and lower bounds
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMhigh'] for _ in range(len(datadict['ratio']))])
    axes[i][1].plot(range(1, len(datadict['ratio']) + 1), [datadict['SMlow'] for _ in range(len(datadict['ratio']))])

    i+=1

print("done")
if len(csv_files) > 0:
    plt.show()




pass

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

pass

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


pass


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


