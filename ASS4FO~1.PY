import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# -------------------------------
# 1. DATA & SETS DEFINITION
# -------------------------------

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

# Production renewables
p_RE = {
    1: 2893.44, 2: 2786.08, 3: 2706.64, 4: 2662.08, 5: 2621.6, 6: 2511.92, 7: 2438.4, 8: 2277.68,
    9: 2071.04, 10: 2014.24, 11: 2091.6, 12: 2208.48, 13: 2252.24, 14: 2303.92, 15: 2542.4,
    16: 3029.92, 17: 3450.4, 18: 3706.0, 19: 3820.16, 20: 3913.28, 21: 4089.6, 22: 4320.16, 
    23: 4414.56, 24: 4360.72, 25: 4192.0, 26: 3830.0, 27: 3329.84, 28: 2814.56, 29: 2480.4,
    30: 2253.04, 31: 2198.24, 32: 2162.64, 33: 2143.68, 34: 2113.2, 35: 2042.24, 36: 2077.12,
    37: 2047.52, 38: 1989.36, 39: 1967.2, 40: 2017.36, 41: 2059.6, 42: 1951.36, 43: 1871.36,
    44: 1817.84, 45: 1704.96, 46: 1499.28, 47: 1235.6, 48: 1026.24, 49: 1013.6, 50: 1296.72,
    51: 1591.52, 52: 1753.76, 53: 1927.28, 54: 2068.24, 55: 2266.64, 56: 2559.12, 57: 3005.28,
    58: 3375.84, 59: 3614.56, 60: 3448.24, 61: 3064.0, 62: 2515.2, 63: 1781.6, 64: 1194.32,
    65: 911.68, 66: 1130.64, 67: 1621.6, 68: 2229.52, 69: 2755.28, 70: 3183.44, 71: 3406.08,
    72: 3613.52, 73: 3717.44, 74: 3684.24, 75: 3560.16, 76: 3337.92, 77: 3032.32, 78: 2366.4,
    79: 1681.2, 80: 1288.64, 81: 1085.84, 82: 1033.44, 83: 1129.36, 84: 1319.44, 85: 1583.04,
    86: 1825.76, 87: 1958.4, 88: 1992.8, 89: 2017.6, 90: 2230.0, 91: 2622.48, 92: 3100.96,
    93: 3413.52, 94: 3490.32, 95: 3497.76, 96: 3643.84, 97: 3587.44, 98: 3480.16, 99: 3349.12,
    100: 3133.92, 101: 3004.4, 102: 2909.12, 103: 2611.6, 104: 2032.8, 105: 1800.48, 106: 1529.84,
    107: 1206.48, 108: 887.6, 109: 770.64, 110: 696.24, 111: 530.72, 112: 297.44, 113: 215.04,
    114: 296.08, 115: 423.28, 116: 596.0, 117: 716.56, 118: 738.24, 119: 730.08, 120: 665.44,
    121: 637.36, 122: 729.52, 123: 992.32, 124: 1427.44, 125: 1923.52, 126: 2323.76, 127: 2646.4,
    128: 2924.24, 129: 3175.12, 130: 3248.88, 131: 3093.76, 132: 2833.36, 133: 2501.76, 134: 2093.2,
    135: 1685.36, 136: 1387.36, 137: 1175.68, 138: 966.08, 139: 812.88, 140: 710.24, 141: 599.36,
    142: 453.76, 143: 337.76, 144: 215.52, 145: 124.0, 146: 74.56, 147: 49.28, 148: 49.84, 
    149: 81.12, 150: 110.88, 151: 103.36, 152: 111.92, 153: 183.68, 154: 322.08, 155: 542.56,
    156: 898.72, 157: 1309.44, 158: 1656.08, 159: 1930.08, 160: 2161.76, 161: 2326.96, 162: 2448.4,
    163: 2503.04, 164: 2509.84, 165: 2579.12, 166: 2760.48, 167: 2962.72, 168: 3173.52
}
# Alpha
alpha_vec = [0, 0.25, 0.33, 0.5, 0.66, 0.75, 1]
# Lambda: cost coefficient for excess production (s_t)
lambda_vec = [1, 10, 100]

# u0: initial on/off state for each plant at time t=0 (parameter; not a decision variable)
u0 = {i: 1 if U1[i] > 0 else 0 for i in plants}

# Initialise results matrix for variety of alphas and lambdas
obj_values_matrix = np.zeros((3,7))
periods_on_matrix = np.full((3, 7), None, dtype=object)
production_matrix = np.full((3,7), None, dtype=object)

for alpha in alpha_vec:
    for lambda_param in lambda_vec:
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
            model.addConstr(gp.quicksum(x[t,i] for i in plants) + alpha * p_RE[t] >= d[t],
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
            model.addConstr(s[t] == gp.quicksum(x[t,i] for i in plants) + alpha * p_RE[t] - d[t],
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
        # Production renewables


        # Remaining demand for each time period after renewables adjustment
        # -------------------------------
        # 7. OUTPUT THE SOLUTION
        # -------------------------------

        plants_on = [0,0,0,0,0,0,0,0]
        plants_production = [0,0,0,0,0,0,0,0]
        
        if model.status == GRB.OPTIMAL:
            print("Objective function value:", model.objVal)
            
            print("Optimal solution found:")
            for t in time_periods:
                print(f"\nTime period {t}:")
                for i in plants:
                    print(f"  Plant {i}: On/Off (u) = {u[t,i].x}, Startup (o) = {o[t,i].x}, Production (x) = {x[t,i].x}")
                    if u[t,i].x == 1:
                        plants_on[i] += 1 
                        plants_production[i] += x[t,i].x
                print(f"  Excess production (s) = {s[t].x}")
        else:
            print("No optimal solution found.")

        periods_on_matrix[lambda_vec.index(lambda_param), alpha_vec.index(alpha)] = plants_on    
        obj_values_matrix[lambda_vec.index(lambda_param), alpha_vec.index(alpha)] = model.objVal
        production_matrix[lambda_vec.index(lambda_param), alpha_vec.index(alpha)] = plants_production

obj_values = pd.DataFrame(obj_values_matrix)
obj_values.to_excel('objective_values.xlsx', index=False, header=False)
periods_on = pd.DataFrame(periods_on_matrix)
periods_on.to_excel('periods_on.xlsx', index=False, header=False)
production_data = pd.DataFrame(production_matrix)
production_data.to_excel('production_data.xlsx', index=False, header=False)
