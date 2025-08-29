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


d = {
    1: 2956.78, 2: 2854.25, 3: 2785.69, 4: 2666.64, 5: 2895.65, 6: 2921.66106367146, 
    7: 3234.16932165577, 8: 3921.54949694522, 9: 3951.95908553903, 10: 4064.41040812598, 
    11: 3691.40653324086, 12: 4118.26182205261, 13: 4005.14514225821, 14: 3696.91271749592, 
    15: 3751.86793827562, 16: 3867.27207157525, 17: 4044.65078970936, 18: 4220.12578013244, 
    19: 4135.18237755747, 20: 3897.85074185100, 21: 3768.47607425841, 22: 3134.41951398254, 
    23: 2763.37998300296, 24: 2346.03705232978, 25: 2220.54, 26: 2137.172, 
    27: 2049.452, 28: 2278.50934979094, 29: 2733.50473226964, 30: 2865.79356878719, 
    31: 3514.39455391973, 32: 3566.76696568051, 33: 3678.56674197249, 34: 4187.22501744920, 
    35: 4173.38077801802, 36: 4035.89044498939, 37: 3735.95241772842, 38: 3638.43254919326, 
    39: 4008.09604852120, 40: 3998.21354335720, 41: 3951.72674557083, 42: 4205.04022415675, 
    43: 3932.42856381876, 44: 4213.07728541017, 45: 3588.40888856601, 46: 3401.16401007052, 
    47: 2773.35886105559, 48: 2424.42720305068, 49: 2202.69, 50: 2195.89, 
    51: 2129.40627135992, 52: 2411.56752611416, 53: 2910.51776234773, 54: 3298.46580701809, 
    55: 3509.47566864365, 56: 3949.95552246179, 57: 3690.52160559648, 58: 3803.24465328376, 
    59: 3703.97435849437, 60: 3789.52626613926, 61: 3778.82481319164, 62: 3727.00777725468, 
    63: 4081.79333466748, 64: 3955.67996816373, 65: 4032.76384574056, 66: 4229.27500241070, 
    67: 3986.76177278712, 68: 4158.44434053456, 69: 3494.45192622668, 70: 3566.58998271626, 
    71: 3008.23104459129, 72: 2260.53750983242, 73: 2100.84, 74: 1980.56, 
    75: 1995.41535656228, 76: 2388.04344190090, 77: 2824.72117895983, 78: 2879.86663068438, 
    79: 3387.36420100758, 80: 3538.89288295781, 81: 4085.57317674655, 82: 4021.17543813205, 
    83: 3849.66643382484, 84: 3656.02255609587, 85: 3739.20037952498, 86: 3754.46326528363, 
    87: 4031.23635595241, 88: 4098.89008194115, 89: 4341.96574451392, 90: 4193.32961183259, 
    91: 3975.88348347853, 92: 4113.07872183372, 93: 3844.43147274461, 94: 3349.52901581044, 
    95: 3007.57947402682, 96: 2411.02826639584, 97: 2371.024, 98: 2088.433, 
    99: 1993.8025, 100: 2115.429, 101: 2447.40218685023, 102: 3166.67316804452, 
    103: 3364.86822979892, 104: 3739.17071509400, 105: 4108.24933125230, 106: 3830.43243031592, 
    107: 3890.20373189816, 108: 4008.93887810695, 109: 3697.28645985072, 110: 3627.87952506268, 
    111: 3806.91044598602, 112: 3855.95862804954, 113: 4363.63304849471, 114: 4364.64139357785, 
    115: 4237.92633387031, 116: 4193.76878134574, 117: 3866.30385716854, 118: 3158.42837508188, 
    119: 3069.59130147988, 120: 2434.25705562698, 121: 1473.04670548367, 122: 1769.95131096098, 
    123: 1797.09988343564, 124: 2072.37626770911, 125: 2547.62023504639, 126: 3059.92883049939, 
    127: 3621.73421007047, 128: 3918.77226006073, 129: 3648.93601612090, 130: 3963.77451776455, 
    131: 3893.78805275587, 132: 3736.88278079007, 133: 3641.73073279018, 134: 3760.80350846584, 
    135: 4140.02115399538, 136: 3938.56926688058, 137: 4154.07046288911, 138: 4311.03966903654, 
    139: 4100.34151526343, 140: 4244.93274253768, 141: 3947.27921837047, 142: 3191.68661592093, 
    143: 2867.98295025512, 144: 2312.64045025655, 145: 1871.2325, 146: 1790.933, 
    147: 1701.2665, 148: 2272.61608804671, 149: 2457.62746528749, 150: 2984.21355506067, 
    151: 3667.76228129299, 152: 3601.97622684015, 153: 3719.28681431652, 154: 3952.91430119155, 
    155: 4183.59017274641, 156: 3747.05598592086, 157: 3923.38852462699, 158: 3977.04577486765, 
    159: 3780.33235243612, 160: 4145.12610934204, 161: 4077.05664348682, 162: 4274.97597360272, 
    163: 4237.99057053805, 164: 4022.56896922812, 165: 3502.47888067774, 166: 3489.28191780051, 
    167: 2777.98404538558, 168: 2254.31695255392
}

# For the initial on/off state at time 0 (used in dynamic constraints)
u0 = {i: 1 if U1[i] > 0 else 0 for i in plants}

# Lambda parameter for excess production cost in the objective
lambda_param = 10

# ===========================================================
# 2. INITIALIZE THE MODEL
# ===========================================================
model = gp.Model("PlantScheduling_Assignment2")
model.setParam('MIPGap', 0.0)
model.setParam('MIPGapAbs', 0.0)

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
x = model.addVars(time_periods, plants, vtype=GRB.CONTINUOUS, lb=0, name="x")

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
    T_init[i] = max(u0[i]*(L[i]-U1[i]), (1 - u0[i])*(l[i]-U0[i]))
    if T_init[i] > 0:
        for t in range(1,T_init[i]+1):
            model.addConstr(u[t,i] == u0[i],
                            name=f"InitStatus_t{t}_Plant{i}")
# (6) Up-Time Constraint:
#     For each plant and each time t, ensure that if a startup occurred in the last L[i] periods,
#     then the plant must be on at time t:
#         sum_{j = max(1, t-L[i]+1)}^{t} v[j,i] <= u[t,i]
for i in plants:
    for t in range(min(T, max((L[i]-U1[i])*u0[i],0)+1), T+1):
        # Determine the starting index for the summation (must be at least 1)
        start = max(1, t - L[i] + 1)
        model.addConstr(gp.quicksum(v[j,i] for j in range(start, t+1)) <= u[t,i],
                        name=f"UpTime_t{t}_Plant{i}")

# (7) Down-Time Constraint:
#     For each plant and each time t, if a shutdown occurred in the last l[i] periods,
#     then the plant must remain off at time t:
#         sum_{j = max(1, t-l[i]+1)}^{t} w[j,i] <= 1 - u[t,i]
for i in plants:
    for t in range(min(T, max((l[i]-U0[i])*(1-u0[i]),0)+1), T+1):
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
