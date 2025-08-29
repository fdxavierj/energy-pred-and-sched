import gurobipy as gp
from gurobipy import GRB

# ===========================================================
# 1. SET PARAMETERS AND SETS
# ===========================================================

# Number of plants (indexed 0 to n-1) and time periods (indexed 1 to T)
n = 8            # Example: 3 plants; update as needed
T = 168            # Example: 5 time periods; update as needed

plants = range(n)           # plants: 0, 1, ..., n-1
time_periods = range(1, T+1)  # time periods: 1, 2, ..., T

# PARAMETERS (replace these example values with your actual data)
q     = {0: 240, 1: 235, 2: 210, 3: 32, 4: 480, 5: 195, 6: 0, 7: 0} # Minimum production for plant i
Q     = {0: 480, 1: 590, 2: 520, 3: 406, 4: 870, 5: 350, 6: 735, 7: 1410} # Maximum production for plant i
L     = {0: 168, 1: 24, 2: 24, 3: 12, 4: 8, 5: 8, 6: 0, 7: 0} # Minimum up time for plant i
l     = {0: 168, 1: 12, 2: 12, 3: 8, 4: 4, 5: 4, 6: 0, 7: 0} # Minimum down time for plant i
c_SU  = {0: 10380, 1: 33590, 2: 0, 3: 23420, 4: 0, 5: 0, 6: 0, 7: 0} # Cost of turning on plant i
c_NL  = {0: 0, 1: 530, 2: 490, 3: 395, 4: 830, 5: 255, 6: 0, 7: 0} # Fixed operating cost for plant i
c_var = {0: 7.7, 1: 16.3, 2: 17, 3: 23.7, 4: 40, 5: 45, 6: 75, 7: 77} # Variable production cost for plant i
U1    = {0: 85, 1: 0, 2: 20, 3: 15, 4: 6, 5: 5, 6: 0, 7: 0} # Periods plant i has been on at t=1
U0    = {0: 0, 1: 10, 2: 0, 3: 0, 4: 0, 5: 0, 6: 3, 7: 12} # Periods plant i has been off at t=1

# Demand for each time period (indexed by t)
d = {1: 2956.78, 2: 2854.25, 3: 2785.69, 4: 2666.64, 5: 2895.65, 6: 2921.66,
    7: 3234.16, 8: 3921.55, 9: 3951.95, 10: 4064.41, 11: 3691.40, 12: 4118.26,
    13: 4005.15, 14: 3696.91, 15: 3751.86, 16: 3867.27, 17: 4044.65, 18: 4220.12,
    19: 4135.18, 20: 3897.85, 21: 3768.47, 22: 3134.41, 23: 2763.37, 24: 2346.03,
    25: 2220.54, 26: 2137.17, 27: 2049.45, 28: 2278.50, 29: 2733.50, 30: 2865.79,
    31: 3514.39, 32: 3566.76, 33: 3678.56, 34: 4187.22, 35: 4173.38, 36: 4035.89,
    37: 3735.95, 38: 3638.43, 39: 4008.09, 40: 3998.21, 41: 3951.72, 42: 4205.04,
    43: 3932.42, 44: 4213.07, 45: 3588.40, 46: 3401.16, 47: 2773.35, 48: 2424.42,
    49: 2202.69, 50: 2195.89, 51: 2129.40, 52: 2411.56, 53: 2910.51, 54: 3298.46,
    55: 3509.47, 56: 3949.95, 57: 3690.52, 58: 3803.24, 59: 3703.97, 60: 3789.52,
    61: 3778.82, 62: 3727.00, 63: 4081.79, 64: 3955.67, 65: 4032.76, 66: 4229.27,
    67: 3986.76, 68: 4158.44, 69: 3494.45, 70: 3566.58, 71: 3008.23, 72: 2260.53,
    73: 2100.84, 74: 1980.56, 75: 1995.41, 76: 2388.04, 77: 2824.72, 78: 2879.86,
    79: 3387.36, 80: 3538.89, 81: 4085.57, 82: 4021.17, 83: 3849.66, 84: 3656.02,
    85: 3739.20, 86: 3754.46, 87: 4031.23, 88: 4098.89, 89: 4341.96, 90: 4193.32,
    91: 3975.88, 92: 4113.07, 93: 3844.43, 94: 3349.52, 95: 3007.57, 96: 2411.02,
    97: 2371.02, 98: 2088.43, 99: 1993.80, 100: 2115.42, 101: 2447.40, 102: 3166.67,
    103: 3364.86, 104: 3739.17, 105: 4108.24, 106: 3830.43, 107: 3890.20, 108: 4008.93,
    109: 3697.28, 110: 3627.87, 111: 3806.91, 112: 3855.95, 113: 4363.63, 114: 4364.64,
    115: 4237.92, 116: 4193.76, 117: 3866.30, 118: 3158.42, 119: 3069.59, 120: 2434.25,
    121: 1473.04, 122: 1769.95, 123: 1797.09, 124: 2072.37, 125: 2547.62, 126: 3059.92,
    127: 3621.73, 128: 3918.77, 129: 3648.93, 130: 3963.77, 131: 3893.78, 132: 3736.88,
    133: 3641.73, 134: 3760.80, 135: 4140.02, 136: 3938.56, 137: 4154.07, 138: 4311.03,
    139: 4100.34, 140: 4244.93, 141: 3947.27, 142: 3191.68, 143: 2867.98, 144: 2312.64,
    145: 1871.23, 146: 1790.93, 147: 1701.26, 148: 2272.61, 149: 2457.62, 150: 2984.21,
    151: 3667.76, 152: 3601.97, 153: 3719.28, 154: 3952.91, 155: 4183.59, 156: 3747.05,
    157: 3923.38, 158: 3977.04, 159: 3780.33, 160: 4145.12, 161: 4077.05, 162: 4274.97,
    163: 4237.99, 164: 4022.56, 165: 3502.47, 166: 3489.28, 167: 2777.98, 168: 2254.31
}

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
    print("Objective function value:", model.objVal)
    
    '''print("Optimal solution found:")
    for t in time_periods:
        print(f"\nTime period {t}:")
        for i in plants:
            print(f"  Plant {i}: On/Off (u) = {u[t,i].x}, Startup (o) = {o[t,i].x}, Production (x) = {x[t,i].x}")
        print(f"  Excess production (s) = {s[t].x}")
else:
    print("No optimal solution found.")'
    '''