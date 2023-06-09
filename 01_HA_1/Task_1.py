from gurobipy import *

# model for task 1
m = Model('task_1')

# production info
car_lb = {'Panda': 120000, 'FIAT_500': 100000, 'Musa': 80000, 'Giulia': 15000}
price = [106000, 136000, 150000, 427000]
salary = [20000, 11000, 20000, 26000]
material = [.57, .6, .55, .45]
manhour = [40, 45, 38, 100]
sale_tax = [.3, .15, .2, .3]
max_money = 4e10 # upper:40000072649, lower:39999991050
max_manhour = 160

# decision variables
x = m.addVars(car_lb, lb=car_lb, vtype=GRB.INTEGER, name='#car production')
y = m.addVars(car_lb, vtype=GRB.INTEGER, name='#employee')

# constraints
# 1. type combination: Panda + Musa <= 300000
m.addConstr(x['Panda'] + x['Musa'] <= 300000)
# 2. total cost: material cost + employee cost <= max money
m.addConstr(sum(
    x[each] * price[i] * material[i] + y[each] * salary[i] * 12
    for i, each in enumerate(car_lb))
            <= max_money)
# 3. production hour: manhour >= demanded hour
m.addConstrs(y[each] * max_manhour * 12 >= x[each] * manhour[i] for i, each in enumerate(car_lb))

# objective: true profit = net profit * (1 - sale_tax) = (gross profit - employee cost) * (1 - sale_tax)
m.setObjective(sum(
    (x[each] * price[i] * (1 - material[i]) - y[each] * salary[i] * 12) * (1 - sale_tax[i])
    for i, each in enumerate(car_lb)), GRB.MAXIMIZE)

# solve
m.optimize()

# display solution
print('\n***** Production solution *****')
for k, v in x.items():
    print(f'{k}: {v.X}')
