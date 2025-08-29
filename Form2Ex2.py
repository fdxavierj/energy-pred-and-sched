import gurobipy as gp
from gurobipy import GRB

# ===========================================================
# 1. SET PARAMETERS AND SETS
# ===========================================================

# Number of plants (indexed 0 to n-1) and time periods (indexed 1 to T)
n = 2            
T = 5            
plants = range(n)              # Plants: 0, 1
time_periods = range(1, T+1)     # Time periods: 1, 2, 3, 4, 5

# PARAMETERS (replace these example values with your actual data)
q     = {0: 20,
         1: 30}     # Minimum production for plant i
Q     = {0: 100, 
         1: 120}     # Maximum production for plant i
L     = {0: 3, 
         1: 2}       # Minimum up time for plant i
l     = {0: 2, 
         1: 3}       # Minimum down time for plant i
c_SU  = {0: 100, 
         1: 120}      # Cost of turning on plant i
c_NL  = {0: 50, 
         1: 60}      # Fixed operating cost for plant i
c_var = {0: 10, 
         1: 8}       # Variable production cost for plant i
U1    = {0: 1, 
         1: 0}       # Periods plant i has been on at t=1
U0    = {0: 0, 
         1: 2}       # Periods plant i has been off at t=1

# Demand for each time period (indexed by t)
d = {1: 100, 
     2: 90, 
     3: 140,
     4: 160,
     5: 140}

# For the initial on/off state at time 0 (used in dynamic constraints)
u0 = {i: 1 if U1[i] > 0 else 0 for i in plants}

# Lambda parameter for excess production cost in the objective
lambda_param = 10

# ===========================================================
# 2. INITIALIZE THE MODEL
# ===========================================================
model = gp.Model("PlantScheduling_Assignment2")

# ===========================================================
# 3. DECISION VARIABLES
# ===========================================================
# Binary variable: u[t,i] = 1 if plant i is on at time t, 0 otherwise.
u = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="u")

# Binary variable: v[t,i] = 1 if plant i is turned on (startup) at time t, 0 otherwise.
v = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="v")

# Binary variable: w[t,i] = 1 if plant i is shut down at time t, 0 otherwise.
w = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="w")

# Integer variable: x[t,i] = production level of plant i at time t (nonnegative integer).
x = model.addVars(time_periods, plants, vtype=GRB.INTEGER, lb=0, name="x")

# Continuous variable: s[t] = excess production at time t (nonnegative).
s = model.addVars(time_periods, vtype=GRB.CONTINUOUS, lb=0, name="s")

# ===========================================================
# 4. OBJECTIVE FUNCTION
# ===========================================================
# Minimize: sum_t { sum_i ( c_var[i]*x[t,i] + c_NL[i]*u[t,i] + c_SU[i]*v[t,i] ) + lambda * s[t] }
model.setObjective(
    gp.quicksum(x[t,i] * c_var[i] + u[t,i] * c_NL[i] + v[t,i] * c_SU[i] for t in time_periods for i in plants)
    + gp.quicksum(lambda_param * s[t] for t in time_periods),
    GRB.MINIMIZE
)

# ===========================================================
# 5. CONSTRAINTS
# ===========================================================

# (1) Demand Constraint: At each time period, total production must meet or exceed demand.
for t in time_periods:
    model.addConstr(gp.quicksum(x[t,i] for i in plants) >= d[t],
                    name=f"Demand_t{t}")

# (2) Production Lower Bound: If a plant is on, production must be at least its minimum.
for t in time_periods:
    for i in plants:
        model.addConstr(x[t,i] >= q[i] * u[t,i],
                        name=f"MinProd_t{t}_Plant{i}")

# (3) Production Upper Bound: Production cannot exceed capacity when the plant is on.
for t in time_periods:
    for i in plants:
        model.addConstr(x[t,i] <= Q[i] * u[t,i],
                        name=f"MaxProd_t{t}_Plant{i}")

# (4) Dynamic Relationship for On/Off Status:
#     u[t,i] - u[t-1,i] = v[t,i] - w[t,i]  for all t and plants.
# For t = 1, use u0[i] as the previous state.
for i in plants:
    # t = 1
    t = 1
    model.addConstr(u[t,i] - u0[i] == v[t,i] - w[t,i],
                    name=f"Dynamic_t{t}_Plant{i}")
    # For t >= 2, use the previous decision variable.
    for t in range(2, T+1):
        model.addConstr(u[t,i] - u[t-1,i] == v[t,i] - w[t,i],
                        name=f"Dynamic_t{t}_Plant{i}")

# (5) Initial Period Consistency:
#     For t = 0,..., T_init, force u[t,i] = u0[i], where
#     T_init[i] = max( u0[i]*(L[i]-U1[i]), (1-u0[i])*(l[i]-U0[i]), 0 ).
T_init = {}
for i in plants:
    T_init[i] = max(u0[i]*(L[i]-U1[i]), (1 - u0[i])*(l[i]-U0[i]), 0)
    # Enforce for t = 1,..., T_init (if T_init >= 1)
    for t in time_periods:
        if t <= T_init[i]:
            model.addConstr(u[t,i] == u0[i],
                            name=f"InitStatus_t{t}_Plant{i}")

# (6) Up-Time Constraint:
#     For each plant and each time t, ensure that if a startup occurred in the last L[i] periods,
#     then the plant must be on at time t:
#         sum_{j = max(1, t-L[i]+1)}^{t} v[j,i] <= u[t,i]
for i in plants:
    for t in time_periods:
        # Determine the starting index for the summation (must be at least 1)
        start = max(1, t - L[i] + 1)
        model.addConstr(gp.quicksum(v[j,i] for j in range(start, t+1)) <= u[t,i],
                        name=f"UpTime_t{t}_Plant{i}")

# (7) Down-Time Constraint:
#     For each plant and each time t, if a shutdown occurred in the last l[i] periods,
#     then the plant must remain off at time t:
#         sum_{j = max(1, t-l[i]+1)}^{t} w[j,i] <= 1 - u[t,i]
for i in plants:
    for t in time_periods:
        start = max(1, t - l[i] + 1)
        model.addConstr(gp.quicksum(w[j,i] for j in range(start, t+1)) <= 1 - u[t,i],
                        name=f"DownTime_t{t}_Plant{i}")

# (8) Excess Production Balance:
#     For each time period, s[t] = (total production) - demand.
for t in time_periods:
    model.addConstr(s[t] == gp.quicksum(x[t,i] for i in plants) - d[t],
                    name=f"Excess_t{t}")

# (9) Variable Domains are already set by the variable definitions:
#     - x[t,i] are nonnegative integers.
#     - u[t,i], v[t,i], w[t,i] are binary.
    
# ===========================================================
# 6. SOLVE THE MODEL
# ===========================================================
model.optimize()

# ===========================================================
# 7. OUTPUT THE SOLUTION
# ===========================================================
if model.status == GRB.OPTIMAL:
    print("Optimal solution found:\n")
    for t in time_periods:
        print(f"Time period {t}:")
        for i in plants:
            print(f"  Plant {i}: u = {u[t,i].x}, v = {v[t,i].x}, w = {w[t,i].x}, x = {x[t,i].x}")
        print(f"  Excess production, s = {s[t].x}\n")
else:
    print("No optimal solution found.")
