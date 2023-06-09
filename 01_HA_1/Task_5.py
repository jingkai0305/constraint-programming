from gurobipy import *

# info
all_inv = ['A', 'B', 'C', 'D', 'E']
gov_pub_ratio = .4
gov_tax = .3
budget = 1e9
a_lim = 1e6
avg_dur = 5
avg_mr = 1.5
M = budget
eps = .01
d = [9, 15, 4, 3, 2]
r = [.045, .054, .051, .044, .061]
t = [0, 0, .3, .3, 0]
mr = [2, 3, 1, 4, 5]

# model for task 5
m = Model('task_5')

# decision variables
x = m.addVars(all_inv, vtype=GRB.CONTINUOUS, name='Investment')  # INTEGER or CONTINUOUS
y = m.addVar(vtype=GRB.BINARY, name='Mutual exclusive for C and D')  # mutual exclusive for C (1) and D (0)
z = m.addVar(vtype=GRB.BINARY, name='Flag for A limitation')  # investment in A >= 1 million (1) or not (0)

# constraints
# 1. total investments <= budget
m.addConstr(sum(x[inv] for inv in all_inv) <= budget)
# 2. government + public ratio >= 40%
m.addConstr(sum(x[inv] / budget for inv in all_inv) >= gov_pub_ratio)
# 3. average duration <= 5
m.addConstr(sum(x[inv] * d[i] / budget for i, inv in enumerate(all_inv)) <= avg_dur)
# 4. average investment risk <= 1.5
m.addConstr(sum(x[inv] * mr[i] / budget for i, inv in enumerate(all_inv)) <= avg_mr)
# 5. C chosen
m.addConstr(x['C'] <= M * z)
# 6. D chosen
m.addConstr(x['D'] <= M * (1 - z))
# 6. if investment in A >= a_lim → z = 1
m.addConstr(x['A'] >= a_lim + eps - M * (1 - z))
# 7. if investment in A < a_lim → z = 0
m.addConstr(x['A'] <= a_lim + M * z)

# objective: maximize total revenues
m.setObjective(sum(x[inv] * r[i] * (1 - t[i]) for i, inv in enumerate(all_inv)), GRB.MAXIMIZE)

# solve
m.optimize()

# display solution (ceiling x with 2 decimals)
print('\n***** Investment solution *****')
for k, v in x.items():
    print(f'{k}: {v.X}')
