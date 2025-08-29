import gurobipy as gp

# Print the Gurobi version
print("Gurobi version:", gp.gurobi.version())

# Try loading the environment to see if the license is valid
try:
    env = gp.Env()
    print("License is valid")
except gp.GurobiError as e:
    print("License issue",e)

    