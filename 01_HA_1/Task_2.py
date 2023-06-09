from gurobipy import *


class Car:
    def __init__(self, type, local_price, material, manhour, salary, sale_tax, min_prod, DI, sale_price, Dm):
        self.type = type
        self.local_price = local_price
        self.material = material
        self.manhour = manhour
        self.salary = salary
        self.sale_tax = sale_tax
        self.min_prod = min_prod
        self.DI = DI
        self.sale_price = sale_price
        self.Dm = Dm


# create 4 types of cars containing all info
panda = Car('Panda', 106000, .57, 40, 20000, .3, 120000,
            {'Poland': 800, 'Italy': 0, 'US': 3500, 'Sweden': 2000},
            {'Poland': 86000, 'Italy': 106000, 'US': 150000, 'Sweden': 112000},
            {'Poland': 75000, 'Italy': 35000, 'US': 40000, 'Sweden': 2000})
fiat_500 = Car('FIAT_500', 136000, .6, 45, 11000, .15, 100000,
               {'Poland': 0, 'Italy': 1000, 'US': 2800, 'Sweden': 1600},
               {'Poland': 92000, 'Italy': 136000, 'US': 170000, 'Sweden': 150000},
               {'Poland': 20000, 'Italy': 40000, 'US': 50000, 'Sweden': 5000})
# N/A in US
musa = Car('Musa', 150000, .55, 38, 20000, .2, 80000,
           {'Poland': 12000, 'Italy': 0, 'US': 0, 'Sweden': 2200},
           {'Poland': 100000, 'Italy': 150000, 'US': 0, 'Sweden': 170000},
           {'Poland': 10000, 'Italy': 80000, 'US': 0, 'Sweden': 1000})
# N/A in Poland
giulia = Car('Giulia', 427000, .45, 100, 26000, .3, 15000,
             {'Poland': 0, 'Italy': 0, 'US': 5000, 'Sweden': 2500},
             {'Poland': 0, 'Italy': 427000, 'US': 550000, 'Sweden': 500000},
             {'Poland': 0, 'Italy': 8000, 'US': 3000, 'Sweden': 1000})

# info
all_car = [panda, fiat_500, musa, giulia]
car_lb = {each_car.type: each_car.min_prod for each_car in all_car}
country = ['Poland', 'Italy', 'US', 'Sweden']
max_money = 4e10
max_manhour = 160
exp_tax = .025

# model for task 2
m = Model('task_2')

# decision variables
x = m.addVars(car_lb, lb=car_lb, vtype=GRB.INTEGER, name='#car production')
y = m.addVars(car_lb, vtype=GRB.INTEGER, name='#employee')
z = m.addVars(country, car_lb, vtype=GRB.INTEGER, name='country - #car sales')

# constraints
# 1. total cost: production cost (material cost + employee cost) + transportation cost + US exp_tax <= max money
m.addConstr(sum(x[each_car.type] * each_car.local_price * each_car.material + y[each_car.type] * each_car.salary * 12
                for each_car in all_car)
            + sum(z[each_country, each_car.type] * each_car.DI[each_country]
                  for each_country in country for each_car in all_car)
            + sum(z['US', each_car.type] * each_car.sale_price['US'] * exp_tax for each_car in all_car)
            <= max_money)
# 2. production hour: manhour >= demanded hour
m.addConstrs(y[each_car.type] * max_manhour * 12 >= x[each_car.type] * each_car.manhour for each_car in all_car)
# 3. sale demand: no. of car_sale >= Dm
m.addConstrs(z[each_country, each_car.type] >= each_car.Dm[each_country]
             for each_country in country for each_car in all_car)
# 4. each car in all countries == each car's production
m.addConstrs(
    sum(z[each_country, each_car.type] for each_country in country) == x[each_car.type] for each_car in all_car)

# objective: true profit = (sales - production cost - transportation cost - exp_tax cost) * (1 - sale_tax) * 4 cars
m.setObjective(sum((sum(z[each_country, each_car.type] * each_car.sale_price[each_country]
                        for each_country in country)
                    - x[each_car.type] * each_car.local_price * each_car.material
                    - y[each_car.type] * each_car.salary * 12
                    - sum(z[each_country, each_car.type] * each_car.DI[each_country]
                          for each_country in country)
                    - z['US', each_car.type] * each_car.sale_price['US'] * exp_tax) * (1 - each_car.sale_tax)
                   for each_car in all_car), GRB.MAXIMIZE)

# solve
m.optimize()

# display solution
print('\n***** Production solution *****')
for k, v in x.items():
    print(f'{k}: {v.X}')

print('\n***** Sales solution *****')
for k, v in z.items():
    info = f' ({k[1]} N/A in {k[0]})' if v.X == 0 else ''
    print(f'{k[0]} - {k[1]}: {v.X}' + info)
