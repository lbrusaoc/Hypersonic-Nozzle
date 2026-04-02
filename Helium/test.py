from pygasflow.solvers import isentropic_solver

results = isentropic_solver("m", 20, gamma=(5/3), to_dict=True)
results.show()