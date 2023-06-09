from z3 import *


def task_3_exhaustive_dijkstra(dist_map, source, sink, path_num, time_limit):
    """
    :param dist_map: type of dict, initial distances every pair of nodes, 1~6: machines, 0: warehouse, 7: delivery
    :param source: type of int, source node
    :param sink: type of int, sink node
    :param path_num: type of int, number of paths to be found
    :param time_limit: type of int, time limit in min
    :return: all_path: all found paths between source and sink containing path value and visited nodes in order
    """

    print(f'Z3 starts solving...\n')

    # params
    num = 8  # number of nodes

    # node list excluding source node and sink node
    nodes = [i for i in range(num)]
    nodes.remove(source)
    nodes.remove(sink)

    # model for task 3 using Z3
    s = Optimize()

    # set time limit in milli sec
    set_option(timeout=int(time_limit * 60 * 1000))

    # decision variable
    x = [Bool(f'Node_{i}') for i in range(num)]
    y = [[Bool(f'Edge_{i}_{j}') for j in range(num)] for i in range(num)]

    # constraints
    # 1. exactly one path from source node
    exactly_one_source = PbEq([(y[k[0]][k[1]], 1) for k in dist_map.keys() if source in k], 1)
    # 2. exactly one path to sink node
    exactly_one_sink = PbEq([(y[k[0]][k[1]], 1) for k in dist_map.keys() if sink in k], 1)
    # 3. for other nodes: exactly two if visit or exactly zero if not visit
    exactly_two = []
    for n in nodes:
        constr = [(Not(x[n]), 2)]
        for k in dist_map.keys():
            if n in k:
                constr.append((y[k[0]][k[1]], 1))
        exactly_two.append(PbEq(constr, 2))

    # objective
    objective = sum([If(y[k[0]][k[1]], v, 0) for k, v in dist_map.items()])

    # add all constraints
    s.add(exactly_one_source)
    s.add(exactly_one_sink)
    s.add(exactly_two)

    # set objective
    s.minimize(objective)

    # exhaustive search path
    all_path, path_ord = {}, 1
    while s.check() == sat and path_ord <= path_num:
        # get values from assigned variable
        m = s.model()

        edge, obj = [], 0
        for k, v in dist_map.items():
            if is_true(m[y[k[0]][k[1]]]):
                edge.append(k)
                obj += v

        # ban this path to find a new shortest path
        s.add(PbLe([(y[k[0]][k[1]], 1) for k in edge], len(edge) - 1))

        # reformat path in visit order
        node_ord, tar, i = [], source, 0
        while i < len(edge):
            if tar in edge[i]:
                node_ord.append(tar)
                tar = edge[i][edge[i].index(tar) - 1]  # get the other node in this edge
                edge.pop(i)
                i = 0
            else:
                i += 1
        node_ord.append(sink)

        # save this path
        node_ord_str = 'Path: '
        for each in node_ord:
            node_ord_str += str(each) + ' -> '
        all_path[path_ord] = (f'Objective: {obj}', node_ord_str[:-4])

        path_ord += 1

    return all_path
