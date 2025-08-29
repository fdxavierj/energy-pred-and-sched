import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import seaborn as sns
import matplotlib.pyplot as plt


# ===========================================================
# 1. DATA & SETS DEFINITION
# ===========================================================

# Number of plants (indexed 0 to n-1) and time periods (indexed 1 to T)
n = 8            
T = 168            

plants = range(n)           # Plants: 0, 1, ..., n-1
time_periods = range(1, T+1)  # Time periods: 1, 2, ..., T

# PARAMETERS (replace these example values with your actual data)
q     = {0: 240, 1: 235, 2: 210, 3: 32, 4: 480, 5: 195, 6: 0, 7: 0}  # Minimum production for plant i
Q     = {0: 480, 1: 590, 2: 520, 3: 406, 4: 870, 5: 350, 6: 735, 7: 1410}  # Maximum production for plant i
L     = {0: 168, 1: 24, 2: 24, 3: 12, 4: 8, 5: 8, 6: 0, 7: 0}  # Minimum up time for plant i
l     = {0: 168, 1: 12, 2: 12, 3: 8, 4: 4, 5: 4, 6: 0, 7: 0}   # Minimum down time for plant i
c_SU  = {0: 10380, 1: 33590, 2: 0, 3: 23420, 4: 0, 5: 0, 6: 0, 7: 0}  # Cost of turning on plant i
c_NL  = {0: 0, 1: 530, 2: 490, 3: 395, 4: 830, 5: 255, 6: 0, 7: 0}  # Fixed operating cost for plant i
c_var = {0: 7.7, 1: 16.3, 2: 17, 3: 23.7, 4: 40, 5: 45, 6: 75, 7: 77}  # Variable production cost for plant i
U1    = {0: 85, 1: 0, 2: 20, 3: 15, 4: 6, 5: 5, 6: 0, 7: 0}  # Periods plant i has been on at t=1
U0    = {0: 0, 1: 10, 2: 0, 3: 0, 4: 0, 5: 0, 6: 3, 7: 12}  # Periods plant i has been off at t=1

scenario1 = {1: 2956.78, 2: 2854.25, 3: 2785.69, 4: 2666.64, 5: 2895.65, 6: 2921.66106367146, 7: 3234.16932165577, 8: 3921.54949694522, 9: 3951.95908553903, 10: 4064.41040812598, 11: 3691.40653324086, 12: 4118.26182205261, 13: 4005.14514225821, 14: 3696.91271749592, 15: 3751.86793827562, 16: 3867.27207157525, 17: 4044.65078970936, 18: 4220.12578013244, 19: 4135.18237755747, 20: 3897.850741851, 21: 3768.47607425841, 22: 3134.41951398254, 23: 2763.37998300296, 24: 2346.03705232978, 25: 2220.54, 26: 2137.172, 27: 2049.452, 28: 2278.50934979094, 29: 2733.50473226964, 30: 2865.79356878719, 31: 3514.39455391973, 32: 3566.76696568051, 33: 3678.56674197249, 34: 4187.2250174492, 35: 4173.38077801802, 36: 4035.89044498939, 37: 3735.95241772842, 38: 3638.43254919326, 39: 4008.0960485212, 40: 3998.2135433572, 41: 3951.72674557083, 42: 4205.04022415675, 43: 3932.42856381876, 44: 4213.07728541017, 45: 3588.40888856601, 46: 3401.16401007052, 47: 2773.35886105559, 48: 2424.42720305068, 49: 2202.69, 50: 2195.89, 51: 2129.40627135992, 52: 2411.56752611416, 53: 2910.51776234773, 54: 3298.46580701809, 55: 3509.47566864365, 56: 3949.95552246179, 57: 3690.52160559648, 58: 3803.24465328376, 59: 3703.97435849437, 60: 3789.52626613926, 61: 3778.82481319164, 62: 3727.00777725468, 63: 4081.79333466748, 64: 3955.67996816373, 65: 4032.76384574056, 66: 4229.2750024107, 67: 3986.76177278712, 68: 4158.44434053456, 69: 3494.45192622668, 70: 3566.58998271626, 71: 3008.23104459129, 72: 2260.53750983242, 73: 2100.84, 74: 1980.56, 75: 1995.41535656228, 76: 2388.0434419009, 77: 2824.72117895983, 78: 2879.86663068438, 79: 3387.36420100758, 80: 3538.89288295781, 81: 4085.57317674655, 82: 4021.17543813205, 83: 3849.66643382484, 84: 3656.02255609587, 85: 3739.20037952498, 86: 3754.46326528363, 87: 4031.23635595241, 88: 4098.89008194115, 89: 4341.96574451392, 90: 4193.32961183259, 91: 3975.88348347853, 92: 4113.07872183372, 93: 3844.43147274461, 94: 3349.52901581044, 95: 3007.57947402682, 96: 2411.02826639584, 97: 2371.024, 98: 2088.433, 99: 1993.8025, 100: 2115.429, 101: 2447.40218685023, 102: 3166.67316804452, 103: 3364.86822979892, 104: 3739.170715094, 105: 4108.2493312523, 106: 3830.43243031592, 107: 3890.20373189816, 108: 4008.93887810695, 109: 3697.28645985072, 110: 3627.87952506268, 111: 3806.91044598602, 112: 3855.95862804954, 113: 4363.63304849471, 114: 4364.64139357785, 115: 4237.92633387031, 116: 4193.76878134574, 117: 3866.30385716854, 118: 3158.42837508188, 119: 3069.59130147988, 120: 2434.25705562698, 121: 1473.04670548367, 122: 1769.95131096098, 123: 1797.09988343564, 124: 2072.37626770911, 125: 2547.62023504639, 126: 3059.92883049939, 127: 3621.73421007047, 128: 3918.77226006073, 129: 3648.9360161209, 130: 3963.77451776455, 131: 3893.78805275587, 132: 3736.88278079007, 133: 3641.73073279018, 134: 3760.80350846584, 135: 4140.02115399538, 136: 3938.56926688058, 137: 4154.07046288911, 138: 4311.03966903654, 139: 4100.34151526343, 140: 4244.93274253768, 141: 3947.27921837047, 142: 3191.68661592093, 143: 2867.98295025512, 144: 2312.64045025655, 145: 1871.2325, 146: 1790.933, 147: 1701.2665, 148: 2272.61608804671, 149: 2457.62746528749, 150: 2984.21355506067, 151: 3667.76228129299, 152: 3601.97622684015, 153: 3719.28681431652, 154: 3952.91430119155, 155: 4183.59017274641, 156: 3747.05598592086, 157: 3923.38852462699, 158: 3977.04577486765, 159: 3780.33235243612, 160: 4145.12610934204, 161: 4077.05664348682, 162: 4274.97597360272, 163: 4237.99057053805, 164: 4022.56896922812, 165: 3502.47888067774, 166: 3489.28191780051, 167: 2777.98404538558, 168: 2254.31695255392}
scenario2 = {1: 929.2, 2: 661.8, 3: 432.84, 4: 282.76, 5: 208.28, 6: 202.4, 7: 210.92, 8: 203.2, 9: 119.84, 10: 97.4, 11: 164.64, 12: 213.88, 13: 211.72, 14: 225.4, 15: 303.28, 16: 472.36, 17: 631.2, 18: 796.92, 19: 972.52, 20: 1098.96, 21: 1265.84, 22: 1417.32, 23: 1601.76, 24: 1833.76, 25: 2146.16, 26: 2438.68, 27: 2619.2, 28: 2745.76, 29: 2817.48, 30: 2839.04, 31: 2845.32, 32: 2848.04, 33: 2848.52, 34: 2847.44, 35: 2835.44, 36: 2784.64, 37: 2746.44, 38: 2721.08, 39: 2720.8, 40: 2713.96, 41: 2683.52, 42: 2646.2, 43: 2602.08, 44: 2540.68, 45: 2486.4, 46: 2430.04, 47: 2378.96, 48: 2333.88, 49: 2313.68, 50: 2374.96, 51: 2422.28, 52: 2506.68, 53: 2609.88, 54: 2676.84, 55: 2725.0, 56: 2750.6, 57: 2774.8, 58: 2787.08, 59: 2793.44, 60: 2795.48, 61: 2788.16, 62: 2759.88, 63: 2714.44, 64: 2678.88, 65: 2661.36, 66: 2657.48, 67: 2653.72, 68: 2653.92, 69: 2670.72, 70: 2689.32, 71: 2702.24, 72: 2724.84, 73: 2756.76, 74: 2781.76, 75: 2795.0, 76: 2810.2, 77: 2821.28, 78: 2826.92, 79: 2824.16, 80: 2820.64, 81: 2827.68, 82: 2829.44, 83: 2813.88, 84: 2807.56, 85: 2820.28, 86: 2824.08, 87: 2811.76, 88: 2788.92, 89: 2763.28, 90: 2752.6, 91: 2755.0, 92: 2740.0, 93: 2727.16, 94: 2700.04, 95: 2661.08, 96: 2665.36, 97: 2703.16, 98: 2702.88, 99: 2689.48, 100: 2685.32, 101: 2663.44, 102: 2584.04, 103: 2484.28, 104: 2501.72, 105: 2591.88, 106: 2687.68, 107: 2796.12, 108: 2842.84, 109: 2848.64, 110: 2848.56, 111: 2848.6, 112: 2848.8, 113: 2848.72, 114: 2848.52, 115: 2848.32, 116: 2848.16, 117: 2848.2, 118: 2848.2, 119: 2848.16, 120: 2848.08, 121: 2847.6, 122: 2847.32, 123: 2846.76, 124: 2846.84, 125: 2847.48, 126: 2847.32, 127: 2847.84, 128: 2848.16, 129: 2848.32, 130: 2848.4, 131: 2848.32, 132: 2848.32, 133: 2848.36, 134: 2841.52, 135: 2799.08, 136: 2739.08, 137: 2714.24, 138: 2720.6, 139: 2740.8, 140: 2786.32, 141: 2751.44, 142: 2802.48, 143: 2843.04, 144: 2845.84, 145: 2840.16, 146: 2776.6, 147: 2563.44, 148: 2230.4, 149: 1845.44, 150: 1395.68, 151: 914.12, 152: 492.44, 153: 225.52, 154: 167.04, 155: 218.68, 156: 355.92, 157: 552.8, 158: 817.2, 159: 1045.08, 160: 1282.04, 161: 1522.92, 162: 1731.92, 163: 1922.24, 164: 2180.52, 165: 2374.2, 166: 2524.88, 167: 2621.92, 168: 2683.72}
scenario3 = {1: 2663.44, 2: 2584.04, 3: 2484.28, 4: 2501.72, 5: 2591.88, 6: 2687.68, 7: 2796.12, 8: 2842.84, 9: 2848.64, 10: 2848.56, 11: 2848.6, 12: 2848.8, 13: 2848.72, 14: 2848.52, 15: 2848.32, 16: 2848.16, 17: 2848.2, 18: 2848.2, 19: 2848.16, 20: 2848.08, 21: 2847.6, 22: 2847.32, 23: 2846.76, 24: 2846.84, 25: 2847.48, 26: 2847.32, 27: 2847.84, 28: 2848.16, 29: 2848.32, 30: 2848.4, 31: 2848.32, 32: 2848.32, 33: 2848.36, 34: 2841.52, 35: 2799.08, 36: 2739.08, 37: 2714.24, 38: 2720.6, 39: 2740.8, 40: 2786.32, 41: 2751.44, 42: 2802.48, 43: 2843.04, 44: 2845.84, 45: 2840.16, 46: 2776.6, 47: 2563.44, 48: 2230.4, 49: 1845.44, 50: 1395.68, 51: 914.12, 52: 492.44, 53: 225.52, 54: 167.04, 55: 218.68, 56: 355.92, 57: 552.8, 58: 817.2, 59: 1045.08, 60: 1282.04, 61: 1522.92, 62: 1731.92, 63: 1922.24, 64: 2180.52, 65: 2374.2, 66: 2524.88, 67: 2621.92, 68: 2683.72, 69: 2709.52, 70: 2680.24, 71: 2640.32, 72: 2693.04, 73: 2751.32, 74: 2743.48, 75: 2670.32, 76: 2577.44, 77: 2479.04, 78: 2295.48, 79: 2021.68, 80: 1806.44, 81: 1617.08, 82: 1554.08, 83: 1564.52, 84: 1743.56, 85: 1903.68, 86: 2038.52, 87: 2171.04, 88: 2265.44, 89: 2195.08, 90: 1994.32, 91: 1721.32, 92: 1476.56, 93: 1169.96, 94: 911.96, 95: 680.36, 96: 472.24, 97: 308.36, 98: 192.64, 99: 83.16, 100: 29.12, 101: 5.48, 102: 0.64, 103: 2.36, 104: 5.64, 105: 7.96, 106: 78.08, 107: 463.84, 108: 905.24, 109: 1315.96, 110: 1688.12, 111: 2026.68, 112: 2346.32, 113: 2545.36, 114: 2680.04, 115: 2779.04, 116: 2819.68, 117: 2839.04, 118: 2843.6, 119: 2847.32, 120: 2848.6, 121: 2848.56, 122: 2848.48, 123: 2848.12, 124: 2845.32, 125: 2839.36, 126: 2826.04, 127: 2761.8, 128: 2661.0, 129: 2552.48, 130: 2430.52, 131: 2186.8, 132: 1861.56, 133: 1574.8, 134: 1348.72, 135: 1191.0, 136: 1108.92, 137: 1294.04, 138: 1733.2, 139: 2236.56, 140: 2510.04, 141: 2650.08, 142: 2782.76, 143: 2840.88, 144: 2848.96, 145: 2848.64, 146: 2844.52, 147: 2840.76, 148: 2817.88, 149: 2741.16, 150: 2651.6, 151: 2597.68, 152: 2556.2, 153: 2545.48, 154: 2663.04, 155: 2574.32, 156: 2654.6, 157: 2807.8, 158: 2842.64, 159: 2848.32, 160: 2848.2, 161: 2846.8, 162: 2841.76, 163: 2830.76, 164: 2808.0, 165: 2761.08, 166: 2662.96, 167: 2553.0, 168:2470.24}
scenario4 = {1: 2004.64, 2: 1928.52, 3: 1900.2, 4: 1925.16, 5: 1915.84, 6: 1865.24, 7: 1841.64, 8: 1941.72, 9: 2005.84, 10: 1989.0, 11: 2065.84, 12: 2121.04, 13: 2096.64, 14: 2113.6, 15: 2227.92, 16: 2456.4, 17: 2654.72, 18: 2771.92, 19: 2830.76, 20: 2846.88, 21: 2841.2, 22: 2840.76, 23: 2840.76, 24: 2840.76, 25: 2848.32, 26: 2848.56, 27: 2817.48, 28: 2728.2, 29: 2624.72, 30: 2588.0, 31: 2632.28, 32: 2705.4, 33: 2699.36, 34: 2662.84, 35: 2635.48, 36: 2668.0, 37: 2698.24, 38: 2717.56, 39: 2738.68, 40: 2749.08, 41: 2756.48, 42: 2765.44, 43: 2772.76, 44: 2780.08, 45: 2795.4, 46: 2803.92, 47: 2797.16, 48: 2782.04, 49: 2748.12, 50: 2704.92, 51: 2645.0, 52: 2635.64, 53: 2661.92, 54: 2678.84, 55: 2684.88, 56: 2710.08, 57: 2747.96, 58: 2785.6, 59: 2814.4, 60: 2825.96, 61: 2827.2, 62: 2824.08, 63: 2805.24, 64: 2785.24, 65: 2759.84, 66: 2720.8, 67: 2708.44, 68: 2716.8, 69: 2736.56, 70: 2778.24, 71: 2801.4, 72: 2820.04, 73: 2829.72, 74: 2833.36, 75: 2835.64, 76: 2837.16, 77: 2836.44, 78: 2835.92, 79: 2831.44, 80: 2819.84, 81: 2806.2, 82: 2793.6, 83: 2793.56, 84: 2798.8, 85: 2797.72, 86: 2788.16, 87: 2767.32, 88: 2748.0, 89: 2735.36, 90: 2699.6, 91: 2662.56, 92: 2644.92, 93: 2615.36, 94: 2570.72, 95: 2522.12, 96: 2448.96, 97: 2372.84, 98: 2277.56, 99: 2260.52, 100: 2230.0, 101: 2139.36, 102: 2052.56, 103: 1981.92, 104: 1809.44, 105: 1424.52, 106: 1047.56, 107: 817.76, 108: 666.0, 109: 550.0, 110: 412.64, 111: 318.16, 112: 282.68, 113: 240.08, 114: 210.4, 115: 180.88, 116: 144.12, 117: 106.48, 118: 59.0, 119: 24.16, 120: 6.36, 121: 1.0, 122: 0.44, 123: 0.44, 124: 0.56, 125: 0.52, 126: 0.08, 127: 2.28, 128: 20.24, 129: 71.36, 130: 172.36, 131: 277.0, 132: 378.72, 133: 463.4, 134: 533.36, 135: 607.6, 136: 739.12, 137: 912.24, 138: 1079.36, 139: 1193.64, 140: 1273.76, 141: 1371.76, 142: 1487.12, 143: 1608.16, 144: 1693.68, 145: 1758.88, 146: 1787.56, 147: 1803.8, 148: 1727.76, 149: 1620.16, 150: 1555.28, 151: 1431.44, 152: 1332.04, 153: 1199.92, 154: 1069.24, 155: 969.0, 156: 1059.48, 157: 1338.0, 158: 1661.16, 159: 1770.64, 160: 1831.36, 161: 1819.36, 162: 1758.12, 163: 1608.2, 164: 1460.44, 165: 1368.4, 166: 1460.0, 167: 1654.72, 168: 1922.28}
scenario5 = {1: 515.32, 2: 550.0, 3: 647.72, 4: 719.44, 5: 785.6, 6: 842.44, 7: 951.52, 8: 1048.2, 9: 1082.48, 10: 1004.76, 11: 869.08, 12: 764.8, 13: 691.76, 14: 651.4, 15: 678.52, 16: 800.76, 17: 956.08, 18: 1062.68, 19: 1182.16, 20: 1146.04, 21: 1063.4, 22: 999.68, 23: 949.4, 24: 976.96, 25: 1012.12, 26: 1182.88, 27: 1336.12, 28: 1354.96, 29: 1309.24, 30: 1220.44, 31: 1148.92, 32: 1103.52, 33: 1070.4, 34: 1046.56, 35: 1002.0, 36: 978.28, 37: 935.88, 38: 907.84, 39: 931.44, 40: 1025.0, 41: 1175.28, 42: 1256.88, 43: 1396.48, 44: 1635.24, 45: 1730.4, 46: 1764.68, 47: 1688.12, 48: 1621.0, 49: 1607.04, 50: 1733.8, 51: 1941.76, 52: 2059.44, 53: 2125.2, 54: 2176.84, 55: 2239.52, 56: 2271.28, 57: 2278.72, 58: 2249.0, 59: 2209.76, 60: 2193.08, 61: 2201.72, 62: 2219.88, 63: 2263.8, 64: 2359.08, 65: 2456.16, 66: 2532.24, 67: 2633.52, 68: 2694.56, 69: 2714.0, 70: 2721.04, 71: 2718.52, 72: 2699.76, 73: 2651.52, 74: 2602.28, 75: 2593.24, 76: 2555.16, 77: 2497.56, 78: 2422.36, 79: 2376.2, 80: 2320.56, 81: 2240.88, 82: 2147.76, 83: 2085.12, 84: 2061.76, 85: 2030.92, 86: 2038.52, 87: 2049.2, 88: 2041.16, 89: 1959.44, 90: 1833.48, 91: 1822.64, 92: 1866.56, 93: 1819.92, 94: 1755.32, 95: 1744.72, 96: 1819.48, 97: 1885.08, 98: 2023.0, 99: 2158.6, 100: 2192.0, 101: 2146.64, 102: 2056.12, 103: 1945.52, 104: 1856.72, 105: 1830.92, 106: 1836.28, 107: 1837.64, 108: 1818.88, 109: 1775.68, 110: 1696.36, 111: 1642.2, 112: 1653.36, 113: 1655.12, 114: 1667.88, 115: 1886.36, 116: 1958.64, 117: 1925.24, 118: 1885.96, 119: 1895.36, 120: 1961.08, 121: 2032.0, 122: 2175.48, 123: 2359.48, 124: 2470.04, 125: 2511.64, 126: 2515.12, 127: 2502.8, 128: 2485.4, 129: 2499.12, 130: 2537.44, 131: 2590.16, 132: 2649.0, 133: 2707.12, 134: 2749.8, 135: 2771.44, 136: 2772.4, 137: 2751.04, 138: 2721.8, 139: 2722.64, 140: 2765.4, 141: 2790.24, 142: 2797.76, 143: 2793.6, 144: 2761.96, 145: 2706.12, 146: 2647.12, 147: 2549.6, 148: 2413.48, 149: 2275.88, 150: 2126.8, 151: 1960.96, 152: 1723.52, 153: 1525.08, 154: 1373.56, 155: 1273.04, 156: 1314.92, 157: 1435.12, 158: 1627.76, 159: 1826.4, 160: 1940.56, 161: 1928.72, 162: 1883.48, 163: 1955.2, 164: 1888.0, 165: 1806.52, 166: 1800.8, 167: 1850.4, 168: 1952.48}

scenario_dict = {
    "Scenario 1": scenario1,
    "Scenario 2": scenario2,
    "Scenario 3": scenario3,
    "Scenario 4": scenario4,
    "Scenario 5": scenario5
}

# p_RE: Production from renewables (or non-dispatchable sources)
# Here p_RE is given as an array of 168 values (one per time period)
p_RE = {t: val for t, val in zip(range(1, T+1), [2893.44, 2786.08, 2706.64, 2662.08, 2621.60, 2511.92, 2438.40, 2277.68, 2071.04, 2014.24, 2091.60, 2208.48, 2252.24, 2303.92, 2542.40, 3029.92, 3450.40, 3706.00, 3820.16, 3913.28, 4089.60, 4320.16, 4414.56, 4360.72, 4192.00, 3830.00, 3329.84, 2814.56, 2480.40, 2253.04, 2198.24, 2162.64, 2143.68, 2113.20, 2042.24, 2077.12, 2047.52, 1989.36, 1967.20, 2017.36, 2059.60, 1951.36, 1871.36, 1817.84, 1704.96, 1499.28, 1235.60, 1026.24, 1013.60, 1296.72, 1591.52, 1753.76, 1927.28, 2068.24, 2266.64, 2559.12, 3005.28, 3375.84, 3614.56, 3448.24, 3064.00, 2515.20, 1781.60, 1194.32, 911.68, 1130.64, 1621.60, 2229.52, 2755.28, 3183.44, 3406.08, 3613.52, 3717.44, 3684.24, 3560.16, 3337.92, 3032.32, 2366.40, 1681.20, 1288.64, 1085.84, 1033.44, 1129.36, 1319.44, 1583.04, 1825.76, 1958.40, 1992.80, 2017.60, 2230.00, 2622.48, 3100.96, 3413.52, 3490.32, 3497.76, 3643.84, 3587.44, 3480.16, 3349.12, 3133.92, 3004.40, 2909.12, 2611.60, 2032.80, 1800.48, 1529.84, 1206.48, 887.60, 770.64, 696.24, 530.72, 297.44, 215.04, 296.08, 423.28, 596.00, 716.56, 738.24, 730.08, 665.44, 637.36, 729.52, 992.32, 1427.44, 1923.52, 2323.76, 2646.40, 2924.24, 3175.12, 3248.88, 3093.76, 2833.36, 2501.76, 2093.20, 1685.36, 1387.36, 1175.68, 966.08, 812.88, 710.24, 599.36, 453.76, 337.76, 215.52, 124.00, 74.56, 49.28, 49.84, 81.12, 110.88, 103.36, 111.92, 183.68, 322.08, 542.56, 898.72, 1309.44, 1656.08, 1930.08, 2161.76, 2326.96, 2448.40, 2503.04, 2509.84, 2579.12, 2760.48, 2962.72, 3173.52])}

# Renewable penetration factors (α) and penalty multipliers (λ)
def generate_alpha_vec(num_alphas):
    """Generate a list of equidistant alpha values from 0 to 1 (inclusive)."""
    if num_alphas < 2:
        raise ValueError("num_alphas must be at least 2.")
    return np.linspace(0, 1, num_alphas).tolist()

num_alphas = 10  # Adjust number of alpha values as needed
alpha_vec = generate_alpha_vec(num_alphas)
lambda_vec = [1, 10, 100]

#-------------------------------
# for HEATMAP ADDITION
#-------------------------------

# Initialize empty lists to store production values for each scenario (columns) and alpha (rows)
num_scenarios = len(scenario_dict)
gas_1_prodcution_lamda_1 = np.empty((num_alphas, num_scenarios), dtype=object)
gas_1_prodcution_lamda_10 = np.empty((num_alphas, num_scenarios), dtype=object)
gas_1_prodcution_lamda_100 = np.empty((num_alphas, num_scenarios), dtype=object)
# ---------------------------------------------------------------------------------------------

# u0: initial on/off state based on U1: if U1 > 0, plant is initially on.
u0 = {i: 1 if U1[i] > 0 else 0 for i in plants}

# For initial period consistency, compute T_init for each plant:
T_init = {}
for i in plants:
    T_init[i] = max(u0[i]*(L[i]-U1[i]), (1-u0[i])*(l[i]-U0[i]), 0)

def run_simulation(scenario_considered, d : dict[float]):
    # ===========================================================
    # 2. SIMULATION LOOP: Run model for each (α, λ) combination using the NEW FORMULATION
    # ===========================================================

    # Initialize matrices to store results
    obj_values_matrix = np.zeros((len(lambda_vec), len(alpha_vec)))
    production_matrix = np.full((len(lambda_vec), len(alpha_vec)), None, dtype=object)
    periods_on_matrix = np.full((len(lambda_vec), len(alpha_vec)), None, dtype=object)
    excess_matrix = np.zeros((len(lambda_vec), len(alpha_vec)))  # total excess production
    startup_counts_matrix = np.full((len(lambda_vec), len(alpha_vec)), None, dtype=object)

    for a in alpha_vec:
        for lam in lambda_vec:
            i_lambda = lambda_vec.index(lam)
            i_alpha = alpha_vec.index(a)
            i_scenario = list(scenario_dict.keys()).index(scenario_considered)
            # -------------------------------
            # MODEL INITIALIZATION (NEW FORMULATION)
            # -------------------------------
            model = gp.Model("PlantScheduling_NewFormulation")
            model.setParam('MIPGap', 0.0)
            model.setParam('MIPGapAbs', 0.0)
            model.setParam('OutputFlag', 0)  # Suppress solver output
            
            # -------------------------------
            # DECISION VARIABLES
            # -------------------------------
            u = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="u")
            v_var = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="v")  # startup indicator
            w = model.addVars(time_periods, plants, vtype=GRB.BINARY, name="w")      # shutdown indicator
            x = model.addVars(time_periods, plants, vtype=GRB.CONTINUOUS, lb=0, name="x")
            s = model.addVars(time_periods, vtype=GRB.CONTINUOUS, lb=0, name="s")
            
            # -------------------------------
            # OBJECTIVE FUNCTION
            # -------------------------------
            model.setObjective(
                gp.quicksum(x[t,i]*c_var[i] + u[t,i]*c_NL[i] + v_var[t,i]*c_SU[i] 
                            for t in time_periods for i in plants) +
                gp.quicksum(lam * s[t] for t in time_periods),
                GRB.MINIMIZE
            )
            
            # -------------------------------
            # CONSTRAINTS
            # -------------------------------
            
            # (1) Demand Constraint with renewable adjustment:
            # Traditional production + a * p_RE[t] must meet demand.
            for t in time_periods:
                model.addConstr(gp.quicksum(x[t,i] for i in plants) + a * p_RE[t] >= d[t],
                                name=f"Demand_t{t}")
            
            # (2) Production Lower Bound: if plant is on, x[t,i] >= q[i]
            for t in time_periods:
                for i in plants:
                    model.addConstr(x[t,i] >= q[i] * u[t,i],
                                    name=f"MinProd_t{t}_Plant{i}")
            
            # (3) Production Upper Bound: if plant is on, x[t,i] <= Q[i]
            for t in time_periods:
                for i in plants:
                    model.addConstr(x[t,i] <= Q[i] * u[t,i],
                                    name=f"MaxProd_t{t}_Plant{i}")
            
            # (4) Dynamic Relationship for On/Off Status:
            # For t=1: u[1,i] - u0[i] = v[1,i] - w[1,i]
            for i in plants:
                t = 1
                model.addConstr(u[t,i] - u0[i] == v_var[t,i] - w[t,i],
                                name=f"Dynamic_t{t}_Plant{i}")
                # For t >=2:
                for t in range(2, T+1):
                    model.addConstr(u[t,i] - u[t-1,i] == v_var[t,i] - w[t,i],
                                    name=f"Dynamic_t{t}_Plant{i}")
            
            # (5) Initial Period Consistency:
            # For t = 1,..., T_init[i], enforce u[t,i] = u0[i]
            for i in plants:
                for t in time_periods:
                    if t <= T_init[i]:
                        model.addConstr(u[t,i] == u0[i],
                                        name=f"InitStatus_t{t}_Plant{i}")
            
            # (6) Up-Time Constraint:
            # For each plant and time t, the sum of startups over the past L[i] periods <= u[t,i]
            for i in plants:
                for t in time_periods:
                    start = max(1, t - L[i] + 1)
                    model.addConstr(gp.quicksum(v_var[j,i] for j in range(start, t+1)) <= u[t,i],
                                    name=f"UpTime_t{t}_Plant{i}")
            
            # (7) Down-Time Constraint:
            # For each plant and time t, the sum of shutdowns over the past l[i] periods <= 1 - u[t,i]
            for i in plants:
                for t in time_periods:
                    start = max(1, t - l[i] + 1)
                    model.addConstr(gp.quicksum(w[j,i] for j in range(start, t+1)) <= 1 - u[t,i],
                                    name=f"DownTime_t{t}_Plant{i}")
            
            # (8) Excess Production Balance:
            # Excess s[t] = (traditional production + a * p_RE[t]) - d[t]
            for t in time_periods:
                model.addConstr(s[t] == gp.quicksum(x[t,i] for i in plants) + a * p_RE[t] - d[t],
                                name=f"Excess_t{t}")
            
            # -------------------------------
            # SOLVE THE MODEL
            # -------------------------------
            model.optimize()
            
            # -------------------------------
            # KPI COLLECTION
            # -------------------------------
            total_excess = 0.0
            plants_on = [0] * n          # count of periods on per plant
            plants_production = [0] * n    # total production per plant
            startup_counts = [0] * n       # total startup count per plant

            if model.status == GRB.OPTIMAL:
                for t in time_periods:
                    total_excess += s[t].x
                    for i in plants:
                        if u[t,i].x >= 0.5:
                            plants_on[i] += 1
                            plants_production[i] += x[t,i].x
                        startup_counts[i] += v_var[t,i].x  # count startup events
                obj_val = model.objVal
            else:
                obj_val = np.nan
            
            # Store results in matrices
            obj_values_matrix[i_lambda, i_alpha] = obj_val
            production_matrix[i_lambda, i_alpha] = plants_production
            periods_on_matrix[i_lambda, i_alpha] = plants_on
            excess_matrix[i_lambda, i_alpha] = total_excess
            startup_counts_matrix[i_lambda, i_alpha] = startup_counts

           # gas_1_prodcution_lamda_1[i_alpha, i_scenario] = list(x[t,4].x for t in time_periods if u[t,4].x >= 0.5)
            if lam == 1:
                gas_1_prodcution_lamda_1[i_alpha, i_scenario] = [x[t, 4].x if not np.isnan(x[t, 4].x) else 0 for t in time_periods]
            elif lam == 10:
                gas_1_prodcution_lamda_10[i_alpha, i_scenario] = [x[t, 4].x if not np.isnan(x[t, 4].x) else 0 for t in time_periods]
            elif lam == 100:
                gas_1_prodcution_lamda_100[i_alpha, i_scenario] = [x[t, 4].x if not np.isnan(x[t, 4].x) else 0 for t in time_periods]
            else:
                raise ValueError("Invalid lambda value.") 


    # Convert results to DataFrames for inspection/export if desired
    obj_values_df = pd.DataFrame(obj_values_matrix, index=lambda_vec, columns=alpha_vec)
    excess_df = pd.DataFrame(excess_matrix, index=lambda_vec, columns=alpha_vec)
    # Note: production_matrix and startup_counts_matrix contain lists.
    print("Objective Values:\n", obj_values_df)	

    # ===========================================================
    # 3. VISUALISATIONS
    # ===========================================================

    # Define plant names corresponding to indices 0 to 7
    plant_names = ['Nuclear', 'Coal 1', 'Coal 2', 'Biomass', 'Gas 1', 'Gas 2', 'CHP 1', 'CHP 2']

    # # Graph 1 (Scenario 1, labda = 1) Generation Mix vs. alpha (Line Chart of Percentage of Total Non-Renewable Production) 
    # # Graph 1 (Scenario X) Generation Mix vs. alpha for Different lambda Values (Line Chart of Percentage of Total Non-Renewable Production) 
    # for i, lam in enumerate(lambda_vec):
    #     plt.figure(figsize=(8, 6))
    #     for plant in plants:
    #         percent_values = []
    #         for j in range(len(alpha_vec)):
    #             total_prod = sum(production_matrix[i, j])
    #             if total_prod > 0:
    #                 percent_value = production_matrix[i, j][plant] / total_prod * 100
    #             else:
    #                 percent_value = 0
    #             percent_values.append(percent_value)
    #         plt.plot(alpha_vec, percent_values, marker='o', label=plant_names[plant])
    #     plt.xlabel('Renewable Penetration Factor (α)')
    #     plt.ylabel('Percentage of Total Production (%)')
    #     plt.title(f'Generation Mix (Percentage) vs. α (λ = {lam}) for {scenario_considered}')
    #     plt.legend()
    #     plt.grid(True)
    #     plt.tight_layout()
    #     plt.show()

    # # Graph 2 (Scenario X) Total System Cost vs. Renewable Penetration (alpha) for Different lambda Values
    # plt.figure(figsize=(8, 6))
    # for i, lam in enumerate(lambda_vec):
    #     plt.plot(alpha_vec, obj_values_matrix[i, :], marker='o', label=f'λ = {lam}')
    #     if lam == 100:  # Highlight the minimum point for λ = 100
    #         min_cost = np.min(obj_values_matrix[i, :])
    #         min_alpha = alpha_vec[np.argmin(obj_values_matrix[i, :])]
    #         plt.scatter(min_alpha, min_cost, color='red', zorder=5, label=f'Min (λ={lam})')
    #         # Add text annotation for the minimum point
    #         plt.annotate(f'({min_alpha:.2f}, {min_cost:.2f})',
    #                     xy=(min_alpha, min_cost),
    #                     xytext=(min_alpha + 0.05, min_cost + 0.05 * min_cost),
    #                     arrowprops=dict(arrowstyle='->', color='gray'),
    #                     fontsize=10, color='black')
    # plt.xlabel('Renewable Penetration Factor (α)')
    # plt.ylabel('Total System Cost')
    # plt.title(f'Total System Cost vs. Renewable Penetration ({scenario_considered})')
    # plt.legend(title='λ Values')
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()



# -------------------------------------
# 4. RUN SIMULATION
# -------------------------------------
for scenario_name, data in scenario_dict.items():
    print(f"Running simulation for {scenario_name}...")
    run_simulation(scenario_name, data)
    print(f"Simulation for {scenario_name} completed.\n")
# -------------------------------------

# -----------PLAYING AROUND WITH THE DATA------------------
data_df = pd.read_excel(r"C:\Users\leoro\OneDrive\Desktop\EUR\YEAR 3\BLOCK 4\Case 1 Operations Research\CODING\POST JEHUM\Realistic Data Demand.xlsx", index_col=0)
print(data_df.head())


rolling_horizon = 30  # Number of periods to consider in the rolling horizon

def calculate_rolling_volatility(data, window):
    """Calculate the standard deviation for each bin of size 'window'."""
    num_bins = len(data) // window
    binned_std = [data[i * window:(i + 1) * window].std() for i in range(num_bins)]
    return pd.Series(binned_std)

rolling_volatility_dict = {i : calculate_rolling_volatility(data_df[i], rolling_horizon) for i in scenario_dict.keys()}  # List to store rolling volatility values
rolling_volatility_array = np.array([rolling_volatility_dict[i] for i in scenario_dict.keys()])  # Convert to numpy array for easier manipulation

# Initialize empty arrays to store rolling production values
gas_1_binned_production_lambda_1 = np.empty((len(alpha_vec), num_scenarios), dtype=object)
gas_1_binned_production_lambda_10 = np.empty((len(alpha_vec), num_scenarios), dtype=object)
gas_1_binned_production_lambda_100 = np.empty((len(alpha_vec), num_scenarios), dtype=object)

for i in range(num_alphas):
    for j in range(num_scenarios):
        gas_1_prodcution_lamda_1[i, j] = []
        gas_1_prodcution_lamda_10[i, j] = []
        gas_1_prodcution_lamda_100[i, j] = []

def calculate_binned_production(data, window):
    binned_sum = [data[i * window:(i + 1) * window].sum() for i in range(len(data) // window)]
    return binned_sum


for a in range(len(alpha_vec)):
    for i in range(len(scenario_dict.keys())):
        gas_1_binned_production_lambda_1[a, i] = calculate_binned_production((np.array(gas_1_prodcution_lamda_1[a, i])), rolling_horizon)
        gas_1_binned_production_lambda_10[a, i] = calculate_binned_production((np.array(gas_1_prodcution_lamda_10[a, i])), rolling_horizon)
        gas_1_binned_production_lambda_100[a, i] = calculate_binned_production((np.array(gas_1_prodcution_lamda_100[a, i])), rolling_horizon)

    # now it is time for the heatmap for each of the 3 different lambdas

    # Initialize dictionaries to store correlation matrices for each lambda
correlation_matrices = {
    1: np.zeros((len(alpha_vec), len(scenario_dict))),
    10: np.zeros((len(alpha_vec), len(scenario_dict))),
    100: np.zeros((len(alpha_vec), len(scenario_dict)))
}

    # Calculate correlations for each lambda
for lam, rolling_production in zip(
    [1, 10, 100],
    [gas_1_binned_production_lambda_1, gas_1_binned_production_lambda_10, gas_1_binned_production_lambda_100]
):
    for a in range(len(alpha_vec)):
        for i, scenario in enumerate(scenario_dict.keys()):
            # Get rolling volatility and rolling production for the current alpha and scenario
            rolling_volatility = rolling_volatility_dict[scenario].dropna().values
            rolling_prod = np.array(rolling_production[a, i])
    
                # Ensure lengths match by trimming the longer array
            min_length = min(len(rolling_volatility), len(rolling_prod))
            rolling_volatility = rolling_volatility[:min_length]
            rolling_prod = rolling_prod[:min_length]
                
                # Debugging: Print trimmed lengths and data
            print(f"Trimmed Rolling Volatility Length: {len(rolling_volatility)}, Trimmed Rolling Production Length: {len(rolling_prod)}")
            print(f"Rolling Volatility Data: {rolling_volatility}")
            print(f"Rolling Production Data: {rolling_prod}")
            

                # Calculate correlation and store it
            if len(rolling_volatility) > 0 and len(rolling_prod) > 0:
                correlation_matrices[lam][a, i] = np.corrcoef(rolling_volatility, rolling_prod)[0, 1]
                # Debugging: Print calculated correlation
                print(f"Correlation: {correlation_matrices[lam][a, i]}")
            else:
                correlation_matrices[lam][a, i] = np.nan  # Handle cases with insufficient data


# Plot heatmaps for each lambda
for lam in [1, 10, 100]:
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        correlation_matrices[lam],
        annot=True,
        fmt=".2f",
        xticklabels=scenario_dict.keys(),
        yticklabels=[f"α={alpha:.2f}" for alpha in alpha_vec],
        cmap="coolwarm",
        cbar_kws={'label': 'Correlation'}
    )
    plt.title(f"Correlation Heatmap (λ = {lam})")
    plt.xlabel("Scenarios")
    plt.ylabel("Renewable Penetration Factor (α)")
    plt.tight_layout()
    plt.show()

