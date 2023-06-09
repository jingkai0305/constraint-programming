from gurobipy import *


class Prod_Line:
    def __init__(self, name, capacity, prod_rate):
        self.name = name
        self.capacity = capacity
        self.prod_rate = prod_rate


# create 4 production lines
pl_1 = Prod_Line('Line 1', 100, {'Component 1': 10, 'Component 2': 15, 'Component 3': 5})
pl_2 = Prod_Line('Line 2', 150, {'Component 1': 15, 'Component 2': 10, 'Component 3': 5})
pl_3 = Prod_Line('Line 3', 80, {'Component 1': 20, 'Component 2': 5, 'Component 3': 10})
pl_4 = Prod_Line('Line 4', 200, {'Component 1': 10, 'Component 2': 15, 'Component 3': 20})

# info
all_pl = [pl_1, pl_2, pl_3, pl_4]
all_line = [pl.name for pl in all_pl]
all_comp = ['Component 1', 'Component 2', 'Component 3']

# model for task 3
m = Model('task_3')

# decision variables
x = m.addVars(all_line, all_comp, vtype=GRB.INTEGER, name='production line - hour')
y = m.addVars(all_comp, vtype=GRB.INTEGER, name='#component')
y_min = m.addVar(vtype=GRB.INTEGER, name='min#component')

# constraints
# 1. prod_rate * hour == #component
m.addConstrs(sum(pl.prod_rate[comp] * x[pl.name, comp] for pl in all_pl) == y[comp] for comp in all_comp)
# 2. total hour for each line <= capacity
m.addConstrs(sum(x[pl.name, comp] for comp in all_comp) <= pl.capacity for pl in all_pl)
# 3. set y_min as minimum #component
m.addConstr(y_min == min_(y[comp] for comp in all_comp))

# objective: maximize minimum #component
m.setObjective(y_min, GRB.MAXIMIZE)

# solve
m.optimize()

# display solution
print('\n***** Production line *****')
for k, v in x.items():
    if v.X != 0:
        print(f'{k[0]} - {k[1]}: {v.X}')

print('\n***** # component *****')
for k, v in y.items():
    print(f'{k}: {v.X}')
