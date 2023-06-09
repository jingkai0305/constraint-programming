from gurobipy import *


def retailers_localization(W, I, F, C, L, U, R, K):
    # model for task 4
    m = Model('task_4')

    # decision variables
    x = m.addVars(len(I), vtype=GRB.BINARY, name='Location')
    y = m.addVars(len(I), vtype=GRB.INTEGER, name='Size')

    # constraints
    # 1. total investment <= W
    m.addConstr(sum(F[i] * x[i] + C[i] * y[i] / 100 for i in range(len(I))) <= W)
    # 2. size_i >= Li
    m.addConstrs(y[i] >= L[i] * x[i] for i in range(len(I)))
    # 3. size_i <= Ui
    m.addConstrs(y[i] <= U[i] * x[i] for i in range(len(I)))
    # 4. K retailers at most
    m.addConstr(sum(x[i] for i in range(len(I))) <= K)

    # objective: maximize total revenues
    m.setObjective(sum(R[i] * y[i] / 100 for i in range(len(I))), GRB.MAXIMIZE)

    # solve
    m.optimize()

    # display solution
    print("\n***** Location: Size *****")
    for i in range(len(I)):
        if x.values()[i].X == 1:
            print(f'{I[i]}: {y.values()[i].X}')


# test case below
W = 55
I = ['Location 1', 'Location 2', 'Location 3', 'Location 4', 'Location 5', 'Location 6']
F = [10, 20, 15, 25, 5, 30]
C = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
L = [100, 110, 120, 130, 140, 150]
U = [200, 210, 220, 230, 240, 250]
R = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
K = 4

retailers_localization(W, I, F, C, L, U, R, K)
