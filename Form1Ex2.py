import gurobipy as gp
from gurobipy import GRB

# -------------------------------
# 1. DATA & SETS DEFINITION
# -------------------------------

# Number of plants (indexed 0 to n-1) and time periods (indexed 1 to T)
n = 2            # Example: 3 plants; update as needed
T = 5            # Example: 5 time periods; update as needed

plants = range(n)           # plants: 0, 1, ..., n-1
time_periods = range(1, T+1)  # time periods: 1, 2, ..., T

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

# u0: initial on/off state for each plant at time t=0 (parameter; not a decision variable)
u0 = {i: 1 if U1[i] > 0 else 0 for i in plants}

# Lambda: cost coefficient for excess production (s_t)
lambda_param = 10

# -------------------------------
# 2. MODEL INITIALIZATION
# -------------------------------
model = gp.Model("PlantScheduling")

# -------------------------------
# 3. DECISION VARIABLES
# -------------------------------
# Binary variables: u[t,i] = 1 if plant i is on at time t, 0 otherwise.
u = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="u")

# Binary variables: o[t,i] = 1 if plant i is turned on at time t.
o = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="o")

# Continuous variables: x[t,i] = production level of plant i at time t, >= 0.
x = model.addVars(time_periods, plants, vtype=GRB.CONTINUOUS, lb=0, name="x")

# Continuous variables: s[t] = excess production at time t, >= 0.
s = model.addVars(time_periods, vtype=GRB.CONTINUOUS, lb=0, name="s")

# -------------------------------
# 4. OBJECTIVE FUNCTION
# -------------------------------
# Minimize: sum over t of [ sum over i (c_var*x + c_NL*u + c_SU*o) + lambda * s ]
model.setObjective(
    gp.quicksum(x[t,i]*c_var[i] + u[t,i]*c_NL[i] + o[t,i]*c_SU[i] 
                for t in time_periods for i in plants) +
    gp.quicksum(lambda_param * s[t] for t in time_periods),
    GRB.MINIMIZE
)

# -------------------------------
# 5. CONSTRAINTS
# -------------------------------

# (1) Demand Constraint: Production must meet or exceed demand at every time period.
for t in time_periods:
    model.addConstr(gp.quicksum(x[t,i] for i in plants) >= d[t],
                    name=f"Demand_t{t}")

# (2) Minimum Production: If plant i is on at time t, then production must be at least q_i.
for t in time_periods:
    for i in plants:
        model.addConstr(x[t,i] >= q[i] * u[t,i],
                        name=f"MinProd_t{t}_p{i}")

# (3) Maximum Production: Production cannot exceed Q_i * u.
for t in time_periods:
    for i in plants:
        model.addConstr(x[t,i] <= Q[i] * u[t,i],
                        name=f"MaxProd_t{t}_p{i}")

# (4) Minimum Up Time (Initial Condition):
#    For each plant i, if it was already on at t=0 (u0), then it must remain on for at least max{L_i - U1[i],0} periods.
for i in plants:
    max_tau = max(L[i] - U1[i], 0)
    # Here, we enforce the condition for time periods 1 up to max_tau.
    for tau in range(1, max_tau+1):
        # u0[i] is given (parameter) so: if u0[i]==1 then u[tau,i] must be 1.
        model.addConstr(u0[i] <= u[tau,i],
                        name=f"MinUpInit_p{i}_tau{tau}")

# (5) Minimum Up Time after startup:
#    For t from max{l_i - U0[i],0}+1 to T, if plant i is turned on at t (i.e., u[t]-u[t-1] = 1),
#    then it must remain on for L_i consecutive periods.
for i in plants:
    start_t = max(l[i] - U0[i], 0) + 1
    for t in range(start_t, T+1):
        # Loop over the next periods tau from t+1 to min{t - 1 + L_i, T}.
        end_tau = min(t - 1 + L[i], T)
        for tau in range(t+1, end_tau+1):
            # If a startup occurs at time t, then u[tau,i] must be 1.
            model.addConstr(u[t,i] - (u[t-1,i] if t > 1 else u0[i]) <= u[tau,i],
                            name=f"MinUp_p{i}_t{t}_tau{tau}")

# (6) Minimum Down Time (Initial Condition):
#    For each plant i, if it was off at t=0 then it must remain off for at least max{l_i - U0[i],0} periods.
for i in plants:
    max_tau = max(l[i] - U0[i], 0)
    for tau in range(1, max_tau+1):
        model.addConstr(1 - u0[i] <= 1 - u[tau,i],
                        name=f"MinDownInit_p{i}_tau{tau}")

# (7) Minimum Down Time after shutdown:
#    For t from max{L_i - U1[i],0}+1 to T, if plant i shuts down (i.e., u[t-1]-u[t] = 1),
#    then it must remain off for l_i consecutive periods.
for i in plants:
    start_t = max(L[i] - U1[i], 0) + 1
    for t in range(start_t, T+1):
        end_tau = min(t - 1 + l[i], T)
        for tau in range(t+1, end_tau+1):
            model.addConstr((u[t-1,i] if t > 1 else u0[i]) - u[t,i] <= 1 - u[tau,i],
                            name=f"MinDown_p{i}_t{t}_tau{tau}")

# (8) Excess Production Balance: Excess equals total production minus demand.
for t in time_periods:
    model.addConstr(s[t] == gp.quicksum(x[t,i] for i in plants) - d[t],
                    name=f"Excess_t{t}")

# (9) Logical Constraints for Startup Decision:
#     a. -o_t^i <= u_{t-1}^i - u_t^i: Ensures o[t,i] captures the startup (transition from off to on)
for t in time_periods:
    for i in plants:
        # For t=1, use the initial state u0[i].
        prev_u = u0[i] if t == 1 else u[t-1,i]
        model.addConstr(-o[t,i] <= prev_u - u[t,i],
                        name=f"StartupLogic1_t{t}_p{i}")

# (10) o[t,i] <= u[t,i]: A plant can only be started if it is on.
for t in time_periods:
    for i in plants:
        model.addConstr(o[t,i] <= u[t,i],
                        name=f"StartupLogic2_t{t}_p{i}")

# (11) o[t,i] <= 1 - u[t-1,i]: A plant can only be started if it was off in the previous period.
for t in time_periods:
    for i in plants:
        prev_u = u0[i] if t == 1 else u[t-1,i]
        model.addConstr(o[t,i] <= 1 - prev_u,
                        name=f"StartupLogic3_t{t}_p{i}")

# Note: The non-negativity of x and s and the binary nature of u and o are already set by variable definitions.

# -------------------------------
# 6. SOLVE THE MODEL
# -------------------------------
model.optimize()

# -------------------------------
# 7. OUTPUT THE SOLUTION
# -------------------------------
if model.status == GRB.OPTIMAL:
    print("Optimal solution found:")
    for t in time_periods:
        print(f"\nTime period {t}:")
        for i in plants:
            print(f"  Plant {i}: On/Off (u) = {u[t,i].x}, Startup (o) = {o[t,i].x}, Production (x) = {x[t,i].x}")
        print(f"  Excess production (s) = {s[t].x}")
else:
    print("No optimal solution found.")
