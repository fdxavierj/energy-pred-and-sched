import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt

# -------------------------------
# 1. DATA & SETS DEFINITION
# -------------------------------

# Number of plants (indexed 0 to n-1) and time periods (indexed 1 to T)
n = 8            
T = 168            

plants = range(n)           # Plants: 0, 1, ..., n-1
time_periods = range(1, T+1)  # Time periods: 1, 2, ..., T

# PARAMETERS
q     = {0: 240, 1: 235, 2: 210, 3: 32, 4: 480, 5: 195, 6: 0, 7: 0}  # Minimum production for plant i
Q     = {0: 480, 1: 590, 2: 520, 3: 406, 4: 870, 5: 350, 6: 735, 7: 1410}  # Maximum production for plant i
L     = {0: 168, 1: 24, 2: 24, 3: 12, 4: 8, 5: 8, 6: 0, 7: 0}  # Minimum up time for plant i
l     = {0: 168, 1: 12, 2: 12, 3: 8, 4: 4, 5: 4, 6: 0, 7: 0}   # Minimum down time for plant i
c_SU  = {0: 10380, 1: 33590, 2: 0, 3: 23420, 4: 0, 5: 0, 6: 0, 7: 0}  # Cost of turning on plant i
c_NL  = {0: 0, 1: 530, 2: 490, 3: 395, 4: 830, 5: 255, 6: 0, 7: 0}  # Fixed operating cost for plant i
c_var = {0: 7.7, 1: 16.3, 2: 17, 3: 23.7, 4: 40, 5: 45, 6: 75, 7: 77}  # Variable production cost for plant i
U1    = {0: 85, 1: 0, 2: 20, 3: 15, 4: 6, 5: 5, 6: 0, 7: 0}  # Periods plant i has been on at t=1
U0    = {0: 0, 1: 10, 2: 0, 3: 0, 4: 0, 5: 0, 6: 3, 7: 12}  # Periods plant i has been off at t=1

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

# Renewable production data for each time period (p_RE[t])
p_RE = {t: val for t, val in zip(range(1, 169), [
    2893.44, 2786.08, 2706.64, 2662.08, 2621.6, 2511.92, 2438.4, 2277.68,
    2071.04, 2014.24, 2091.6, 2208.48, 2252.24, 2303.92, 2542.4, 3029.92,
    3450.4, 3706.0, 3820.16, 3913.28, 4089.6, 4320.16, 4414.56, 4360.72,
    4192.0, 3830.0, 3329.84, 2814.56, 2480.4, 2253.04, 2198.24, 2162.64,
    2143.68, 2113.2, 2042.24, 2077.12, 2047.52, 1989.36, 1967.2, 2017.36,
    2059.6, 1951.36, 1871.36, 1817.84, 1704.96, 1499.28, 1235.6, 1026.24,
    1013.6, 1296.72, 1591.52, 1753.76, 1927.28, 2068.24, 2266.64, 2559.12,
    3005.28, 3375.84, 3614.56, 3448.24, 3064.0, 2515.2, 1781.6, 1194.32,
    911.68, 1130.64, 1621.6, 2229.52, 2755.28, 3183.44, 3406.08, 3613.52,
    3717.44, 3684.24, 3560.16, 3337.92, 3032.32, 2366.4, 1681.2, 1288.64,
    1085.84, 1033.44, 1129.36, 1319.44, 1583.04, 1825.76, 1958.4, 1992.8,
    2017.6, 2230.0, 2622.48, 3100.96, 3413.52, 3490.32, 3497.76, 3643.84,
    3587.44, 3480.16, 3349.12, 3133.92, 3004.4, 2909.12, 2611.6, 2032.8,
    1800.48, 1529.84, 1206.48, 887.6, 770.64, 696.24, 530.72, 297.44,
    215.04, 296.08, 423.28, 596.0, 716.56, 738.24, 730.08, 665.44,
    637.36, 729.52, 992.32, 1427.44, 1923.52, 2323.76, 2646.4, 2924.24,
    3175.12, 3248.88, 3093.76, 2833.36, 2501.76, 2093.2, 1685.36, 1387.36,
    1175.68, 966.08, 812.88, 710.24, 599.36, 453.76, 337.76, 215.52,
    124.0, 74.56, 49.28, 49.84, 81.12, 110.88, 103.36, 111.92,
    183.68, 322.08, 542.56, 898.72, 1309.44, 1656.08, 1930.08, 2161.76,
    2326.96, 2448.4, 2503.04, 2509.84, 2579.12, 2760.48, 2962.72, 3173.52
])}

# Renewable penetration factors (α) and penalty multipliers (λ)
alpha_vec = [0, 0.25, 0.33, 0.5, 0.66, 0.75, 1]
lambda_vec = [1, 10, 100]

# u0: initial on/off state (if U1 > 0, plant is considered on initially)
u0 = {i: 1 if U1[i] > 0 else 0 for i in plants}

# Initialize matrices to store results (dimensions: len(lambda_vec) x len(alpha_vec))
obj_values_matrix = np.zeros((len(lambda_vec), len(alpha_vec)))
production_matrix = np.full((len(lambda_vec), len(alpha_vec)), None, dtype=object)
periods_on_matrix = np.full((len(lambda_vec), len(alpha_vec)), None, dtype=object)
excess_matrix = np.zeros((len(lambda_vec), len(alpha_vec)))  # total excess production
startup_counts_matrix = np.full((len(lambda_vec), len(alpha_vec)), None, dtype=object)

# -------------------------------
# 2. SIMULATION LOOP: Run model for each (α, λ) combination
# -------------------------------
for a in alpha_vec:
    for lam in lambda_vec:
        # Set indices for storing results
        i_lambda = lambda_vec.index(lam)
        i_alpha = alpha_vec.index(a)
        
        # -------------------------------
        # MODEL INITIALIZATION
        # -------------------------------
        model = gp.Model("PlantScheduling")
        model.setParam('OutputFlag', 0)  # turn off solver output
        
        # -------------------------------
        # DECISION VARIABLES
        # -------------------------------
        u = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="u")
        o = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="o")
        x = model.addVars(time_periods, plants, vtype=GRB.CONTINUOUS, lb=0, name="x")
        s = model.addVars(time_periods, vtype=GRB.CONTINUOUS, lb=0, name="s")
        
        # -------------------------------
        # OBJECTIVE FUNCTION
        # -------------------------------
        model.setObjective(
            gp.quicksum(x[t,i]*c_var[i] + u[t,i]*c_NL[i] + o[t,i]*c_SU[i]
                        for t in time_periods for i in plants) +
            gp.quicksum(lam * s[t] for t in time_periods),
            GRB.MINIMIZE
        )
        
        # -------------------------------
        # CONSTRAINTS
        # -------------------------------
        
        # (1) Demand Constraint with renewables adjustment: traditional production + a·p_RE[t] >= d[t]
        for t in time_periods:
            model.addConstr(gp.quicksum(x[t,i] for i in plants) + a * p_RE[t] >= d[t],
                            name=f"Demand_t{t}")
            
        # (2) Minimum Production: if plant is on, production >= q
        for t in time_periods:
            for i in plants:
                model.addConstr(x[t,i] >= q[i] * u[t,i],
                                name=f"MinProd_t{t}_p{i}")
                
        # (3) Maximum Production: production <= Q[i] * u
        for t in time_periods:
            for i in plants:
                model.addConstr(x[t,i] <= Q[i] * u[t,i],
                                name=f"MaxProd_t{t}_p{i}")
                
        # (4) Minimum Up Time (Initial Condition)
        for i in plants:
            max_tau = max(L[i] - U1[i], 0)
            for tau in range(1, max_tau+1):
                model.addConstr(u0[i] <= u[tau,i],
                                name=f"MinUpInit_p{i}_tau{tau}")
                
        # (5) Minimum Up Time after startup
        for i in plants:
            start_t = max(l[i] - U0[i], 0) + 1
            for t in range(start_t, T+1):
                end_tau = min(t - 1 + L[i], T)
                for tau in range(t+1, end_tau+1):
                    model.addConstr(u[t,i] - (u[t-1,i] if t > 1 else u0[i]) <= u[tau,i],
                                    name=f"MinUp_p{i}_t{t}_tau{tau}")
                
        # (6) Minimum Down Time (Initial Condition)
        for i in plants:
            max_tau = max(l[i] - U0[i], 0)
            for tau in range(1, max_tau+1):
                model.addConstr(1 - u0[i] <= 1 - u[tau,i],
                                name=f"MinDownInit_p{i}_tau{tau}")
                
        # (7) Minimum Down Time after shutdown
        for i in plants:
            start_t = max(L[i] - U1[i], 0) + 1
            for t in range(start_t, T+1):
                end_tau = min(t - 1 + l[i], T)
                for tau in range(t+1, end_tau+1):
                    model.addConstr((u[t-1,i] if t > 1 else u0[i]) - u[t,i] <= 1 - u[tau,i],
                                    name=f"MinDown_p{i}_t{t}_tau{tau}")
                
        # (8) Excess Production Balance: s[t] = (total traditional production + a·p_RE[t]) - d[t]
        for t in time_periods:
            model.addConstr(s[t] == gp.quicksum(x[t,i] for i in plants) + a * p_RE[t] - d[t],
                            name=f"Excess_t{t}")
                
        # (9) Startup logical constraints
        for t in time_periods:
            for i in plants:
                prev_u = u0[i] if t == 1 else u[t-1,i]
                model.addConstr(-o[t,i] <= prev_u - u[t,i],
                                name=f"StartupLogic1_t{t}_p{i}")
        for t in time_periods:
            for i in plants:
                model.addConstr(o[t,i] <= u[t,i],
                                name=f"StartupLogic2_t{t}_p{i}")
        for t in time_periods:
            for i in plants:
                prev_u = u0[i] if t == 1 else u[t-1,i]
                model.addConstr(o[t,i] <= 1 - prev_u,
                                name=f"StartupLogic3_t{t}_p{i}")
                
        # -------------------------------
        # SOLVE THE MODEL
        # -------------------------------
        model.optimize()
        
        # Initialize KPI collectors
        total_excess = 0.0
        plants_on = [0] * n          # counts of periods on per plant
        plants_production = [0] * n    # total production per plant
        startup_counts = [0] * n       # sum of startup indicator values per plant
        
        if model.status == GRB.OPTIMAL:
            for t in time_periods:
                total_excess += s[t].x
                for i in plants:
                    if u[t,i].x >= 0.5:
                        plants_on[i] += 1
                        plants_production[i] += x[t,i].x
                    startup_counts[i] += o[t,i].x
            obj_val = model.objVal
        else:
            obj_val = np.nan
            
        # Store results in matrices
        obj_values_matrix[i_lambda, i_alpha] = obj_val
        production_matrix[i_lambda, i_alpha] = plants_production
        periods_on_matrix[i_lambda, i_alpha] = plants_on
        excess_matrix[i_lambda, i_alpha] = total_excess
        startup_counts_matrix[i_lambda, i_alpha] = startup_counts

# Convert results to DataFrames (for possible export or inspection)
obj_values_df = pd.DataFrame(obj_values_matrix, index=lambda_vec, columns=alpha_vec)
excess_df = pd.DataFrame(excess_matrix, index=lambda_vec, columns=alpha_vec)
# production_matrix and startup_counts_matrix are arrays of lists

# -------------------------------
# 3. VISUALISATIONS
# -------------------------------

# Graph 1: Total System Cost vs. Renewable Penetration (α) for Different λ Values
plt.figure(figsize=(8, 6))
for i, lam in enumerate(lambda_vec):
    plt.plot(alpha_vec, obj_values_matrix[i, :], marker='o', label=f'λ = {lam}')
plt.xlabel('Renewable Penetration Factor (α)')
plt.ylabel('Total System Cost')
plt.title('Total System Cost vs. Renewable Penetration for Different λ Values')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Graph 2: Generation Mix vs. α for Different λ Values (Stacked Bar Chart)
# For each λ, create a separate figure showing total production per plant (stacked)
for i, lam in enumerate(lambda_vec):
    fig, ax = plt.subplots(figsize=(8, 6))
    bar_width = 0.023  # Adjust the width of the bars
    bottom = np.zeros(len(alpha_vec))
    for plant in plants:
        # Extract production values for current plant over all α for this λ
        prod_values = [production_matrix[i, j][plant] for j in range(len(alpha_vec))]
        ax.bar(alpha_vec, prod_values, width=bar_width, bottom=bottom, label=f'Plant {plant}')
        bottom += np.array(prod_values)
    ax.set_xlabel('Renewable Penetration Factor (α)')
    ax.set_ylabel('Total Production by Traditional Plants')
    ax.set_title(f'Generation Mix vs. α (λ = {lam})')
    ax.legend()
    plt.tight_layout()
    plt.show()

# Graph 2.5: Generation Mix vs. α for Different λ Values (Line Chart version)
for i, lam in enumerate(lambda_vec):
    plt.figure(figsize=(8, 6))
    for plant in plants:
        # Extract production values for the current plant over all α for this λ
        prod_values = [production_matrix[i, j][plant] for j in range(len(alpha_vec))]
        plt.plot(alpha_vec, prod_values, marker='o', label=f'Plant {plant}')
    plt.xlabel('Renewable Penetration Factor (α)')
    plt.ylabel('Total Production by Traditional Plants')
    plt.title(f'Generation Mix vs. α (λ = {lam})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Graph 2.75: Generation Mix vs. α for Different λ Values (Line Chart of Percentage of Total Production)
for i, lam in enumerate(lambda_vec):
    plt.figure(figsize=(8, 6))
    for plant in plants:
        percent_values = []
        for j in range(len(alpha_vec)):
            # Total production across all plants for the given λ and α
            total_prod = sum(production_matrix[i, j])
            # Avoid division by zero
            if total_prod > 0:
                percent_value = production_matrix[i, j][plant] / total_prod * 100
            else:
                percent_value = 0
            percent_values.append(percent_value)
        plt.plot(alpha_vec, percent_values, marker='o', label=f'Plant {plant}')
    plt.xlabel('Renewable Penetration Factor (α)')
    plt.ylabel('Percentage of Total Production (%)')
    plt.title(f'Generation Mix (Percentage) vs. α (λ = {lam})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Graph 3: Excess Production vs. α for Different λ Values
plt.figure(figsize=(8, 6))
for i, lam in enumerate(lambda_vec):
    plt.plot(alpha_vec, excess_matrix[i, :], marker='s', label=f'λ = {lam}')
plt.xlabel('Renewable Penetration Factor (α)')
plt.ylabel('Total Excess Production')
plt.title('Excess Production vs. Renewable Penetration for Different λ Values')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Graph 4: Startup Counts vs. α for Different Plants (for each λ value)
for i, lam in enumerate(lambda_vec):
    plt.figure(figsize=(8, 6))
    for plant in plants:
        # Extract startup counts for current plant over all α for this λ
        startup_vals = [startup_counts_matrix[i, j][plant] for j in range(len(alpha_vec))]
        plt.plot(alpha_vec, startup_vals, marker='^', label=f'Plant {plant}')
    plt.xlabel('Renewable Penetration Factor (α)')
    plt.ylabel('Total Startup Counts')
    plt.title(f'Startup Counts vs. α (λ = {lam})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
