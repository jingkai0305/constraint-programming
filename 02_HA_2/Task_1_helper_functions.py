import time
import gurobipy as gb
import z3
import numpy as np


def task_1_gurobi(case, time_limit):
    """
    solver for a single test case in a variable size using gurobi
    :param case: type of Test_case
    :param time_limit: type of int, time limit for the solver in min
    :return: None (in-place modification on case.obj and case.sch)
    """

    print(f'Gurobi starts solving {case.name}...\n')

    # compute execution time
    start_time = time.time()

    # model for task 1 using gurobi
    m = gb.Model('task_1_gurobi')

    # set time limit in sec
    m.Params.TimeLimit = int(time_limit * 60)

    # decision variable
    x = m.addVars(case.size[0], case.size[1], vtype=gb.GRB.INTEGER, name='start time')
    y = m.addVars(case.size[0], case.size[0], case.size[1], vtype=gb.GRB.BINARY,
                  name='mutual exclusion for each pair of jobs on each machine')
    z = m.addVar(vtype=gb.GRB.INTEGER, name='total execution time')

    # big-M
    M = case.pt.max() * case.size[0] * case.size[1]

    # constraints
    # 1. for each job: start time + processing time <= next start time
    m.addConstrs(x[i, case.po[i, j]] + case.pt[i, case.po[i, j]] <= x[i, case.po[i, j + 1]]
                 for i in range(case.size[0])
                 for j in range(case.size[1] - 1))
    # 2. for each job: the last start time + processing time <= total execution time
    m.addConstrs(x[i, case.po[i, -1]] + case.pt[i, case.po[i, -1]] <= z for i in range(case.size[0]))
    # 3. mutual exclusion for each machine: x_i ends before x_j starts -> y = 0
    m.addConstrs(x[i, m] + case.pt[i, m] <= x[j, m] + M * y[i, j, m]
                 for m in range(case.size[1])
                 for i in range(case.size[0])
                 for j in range(case.size[0])
                 if i != j)
    # 4. mutual exclusion for each machine: x_i starts after x_j ends -> y = 1
    m.addConstrs(x[i, m] >= x[j, m] + case.pt[j, m] - M * (1 - y[i, j, m])
                 for m in range(case.size[1])
                 for i in range(case.size[0])
                 for j in range(case.size[0])
                 if i != j)

    # objective: minimize total execution time
    m.setObjective(z, gb.GRB.MINIMIZE)

    # solve
    m.optimize()

    # execution time
    et = time.time() - start_time
    # in-place modify case
    case.slv = 'Gurobi'
    case.time = f'{int(et / 60)} min {int(et % 60)} sec {int(1e3 * et % 1e3)} ms'
    try:
        case.obj = int(z.X)
    except:
        case.obj = f'No solution found within {time_limit} min'
    try:
        case.sch = np.zeros(case.size, dtype=int)
        for k, v in x.items():
            case.sch[k[0], k[1]] = v.X
    except:
        case.sch = f'No solution found within {time_limit} min'


def task_1_z3(case, time_limit):
    """
    solver for a single test case in a variable size using z3
    :param case: type of Test_case
    :param time_limit: type of int, time limit for the solver in min
    :return: None (in-place modification on case.obj and case.sch)
    """

    print(f'Z3 starts solving {case.name}...\n')

    # compute execution time
    start_time = time.time()

    # model for task 1 using Z3
    s = z3.Optimize()

    # set time limit in milli sec
    z3.set_option(timeout=int(time_limit * 60 * 1000))

    # decision variable
    x = [[z3.Int(f'x_{i}_{j}') for j in range(case.size[1])] for i in range(case.size[0])]  # start time
    obj = z3.Int('obj')  # total execution time

    # domain of decision variable
    d = case.pt.sum() - case.pt.min()
    domain = [z3.And(0 <= x[i][j], x[i][j] <= d.item()) for i in range(case.size[0]) for j in range(case.size[1])]

    # constraints
    # 1. processing order
    processing_order = [x[i][case.po[i, j].item()] + case.pt[i, case.po[i, j].item()].item() <=
                        x[i][case.po[i, j + 1].item()]
                        for i in range(case.size[0])
                        for j in range(case.size[1] - 1)]
    # 2. mutual exclusion
    mutual_exclusion = [z3.Or(x[i][m] + case.pt[i, m].item() <= x[j][m], x[i][m] >= x[j][m] + case.pt[j, m].item())
                        for m in range(case.size[1])
                        for i in range(case.size[0] - 1)
                        for j in range(i + 1, case.size[0])]

    # objective
    objective = [x[i][case.po[i, -1].item()] + case.pt[i, case.po[i, -1].item()].item() <= obj
                 for i in range(case.size[0])]

    # add all constraints
    s.add(domain + processing_order + mutual_exclusion + objective)

    # solve
    s.minimize(obj)
    s.check()

    # execution time
    et = time.time() - start_time

    # in-place modify case
    case.slv = 'Z3'
    case.time = f'{int(et / 60)} min {int(et % 60)} sec {int(1e3 * et % 1e3)} ms'
    try:
        case.obj = s.model()[obj].as_long()
    except:
        case.obj = f'No solution found within {time_limit} min'
    try:
        case.sch = np.zeros(case.size, dtype=int)
        for i in range(case.size[0]):
            for j in range(case.size[1]):
                case.sch[i][j] = s.model()[x[i][j]].as_long()
    except:
        case.sch = f'No solution found within {time_limit} min'
