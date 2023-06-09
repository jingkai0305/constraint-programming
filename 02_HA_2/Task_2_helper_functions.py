from gurobipy import *
import numpy as np


def task_2_a_star(dist_map, h, source, sink):
    '''
    A star solver for task 2 using gurobi
    :param dist_map: type of dict, known shortest distance from one node to all others
    :param h: type of dict, heuristic
    :param source: type of int, source node
    :param sink: type of int, sink node
    :return: None (in-place modify dist_map with new shortest path values)
    '''

    # number of nodes
    num = 8

    # node list excluding source node and sink node
    nodes = [i for i in range(num)]
    nodes.remove(source)
    nodes.remove(sink)

    # model for task 1 A start implementation using gurobi
    m = Model('task_2_a_star')

    # decision variable
    x = {k: m.addVar(vtype=GRB.BINARY, name=f'x_{k[0]}_{k[1]}') for k in dist_map.keys()}

    # constraints
    # 1. one and only one path from source node
    m.addConstr(sum(x[k] for k in x.keys() if source == k[0]) == 1, name='one path from source node')
    # 2. one and only one path to sink node
    m.addConstr(sum(x[k] for k in x.keys() if sink == k[1]) == 1, name='one path to sink node')
    # 3. for each intermediate node: inflow == outflow (if go into this node, must go out from this node)
    m.addConstrs((sum(x[k] for k in x.keys() if n == k[1]) == sum(x[k] for k in x.keys() if n == k[0])
                  for n in nodes), name='inflow == outflow')

    # objective: minimize the path from source node (the first element in ord_list) to sink node (the last element)
    m.setObjective(sum(x[k] * (v + h[k[1], sink]) for k, v in dist_map.items()), GRB.MINIMIZE)

    # solve
    m.optimize()

    # compute shortest path value from source node to sink node
    sp = 0
    for k, v in x.items():
        if v.X:
            sp += dist_map[k]

    # in-place modify dist_map
    dist_map[source, sink] = dist_map[sink, source] = sp


def task_2_gurobi(case, time_limit, tt_map):
    """
    solver for a single test case in a variable size using gurobi
    :param case: type of Test_case
    :param time_limit: type of int, time limit for the solver in min
    :param tt_map: shortest transportation time in second, 0~5: machines, 6: delivery, -1: warehouse
    :return: None (in-place modification on case.obj and case.sch)
    """

    print(f'Gurobi starts solving {case.name}...\n')

    # model for task 2 using gurobi
    m = Model('task_2_gurobi')

    # set time limit in sec
    m.Params.TimeLimit = int(time_limit * 60)

    # decision variable
    x = m.addVars(case.size[0], case.size[1], vtype=GRB.CONTINUOUS, name='start time')
    y = m.addVars(case.size[0], case.size[0], case.size[1], vtype=GRB.BINARY,
                  name='mutual exclusion for each pair of jobs on each machine')
    z = m.addVar(vtype=GRB.INTEGER, name='total execution time')

    # big-M
    M = (case.pt.max() + max(tt_map.values())) * case.size[0] * case.size[1]

    # constraints
    # 1. for each job: start time >= transportation time from warehouse to the first machine
    m.addConstrs(x[i, case.po[i, 0]] >= tt_map[-1, case.po[i, 0]] for i in range(case.size[0]))
    # 2. for each job: start time + processing time + transportation time <= next start time
    m.addConstrs(x[i, case.po[i, j]] + case.pt[i, case.po[i, j]] + tt_map[case.po[i, j], case.po[i, j + 1]] <=
                 x[i, case.po[i, j + 1]]
                 for i in range(case.size[0])
                 for j in range(case.size[1] - 1))
    # 3. for each job: the last start time + processing time + transportation time to delivery <= total execution time
    m.addConstrs(x[i, case.po[i, -1]] + case.pt[i, case.po[i, -1]] + tt_map[case.po[i, -1], 6] <= z
                 for i in range(case.size[0]))
    # 4. mutual exclusion for each machine: x_i ends before x_j starts -> y = 0
    m.addConstrs(x[i, m] + case.pt[i, m] <= x[j, m] + M * y[i, j, m]
                 for m in range(1, case.size[1])
                 for i in range(case.size[0] - 1)
                 for j in range(i + 1, case.size[0]))
    # 5. mutual exclusion for each machine: x_i starts after x_j ends -> y = 1
    m.addConstrs(x[i, m] >= x[j, m] + case.pt[j, m] - M * (1 - y[i, j, m])
                 for m in range(case.size[1])
                 for i in range(case.size[0] - 1)
                 for j in range(i + 1, case.size[0]))

    # objective: minimize total execution time
    m.setObjective(z, GRB.MINIMIZE)

    # solve
    m.optimize()

    # in-place modify case
    case.slv = 'Gurobi'
    try:
        case.obj = z.X
    except:
        case.obj = f'No solution found within {time_limit} min'
    try:
        case.sch = np.zeros(case.size)
        for k, v in x.items():
            case.sch[k[0], k[1]] = v.X
    except:
        case.sch = f'No solution found within {time_limit} min'
