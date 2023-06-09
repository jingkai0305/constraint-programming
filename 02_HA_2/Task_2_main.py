from Read_test_case import *
from Task_2_helper_functions import *

# numpy is needed in helper functions

# select test cases from folder "Test case", see details in Read_test_case.py
case_name = ['tf06']

# read all required test cases into a list containing Test_case objects
test_case = read_test_case(case_name)

# params
time_limit = 20  # time limit for solver in min
dtl_flag = True  # detail flag of Test_case, True for detailed info, False for solution only when printing

# info
spd = 5  # transportation speed, 5 m/s
x_dist = [7, 21, 25, 20, 18, 28, 8]  # x-direction distance of shop floor, left to right, in meter
y_dist = [17, 17, 17, 19]  # y-direction distance of shop floor, bottom to top, in meter
# known shortest distance from a node to others, 1~6: machines, 0: warehouse, 7: delivery
dist_map = {(0, 1): sum(x_dist[:4]) + y_dist[2],
            (0, 2): sum(x_dist[:3]) + 2 * y_dist[0] + y_dist[1],
            (0, 3): sum(x_dist[:5]) + 2 * y_dist[0] + y_dist[1],
            (0, 4): sum(x_dist[:2]) + sum(y_dist[2:]),
            (0, 5): sum(x_dist[:2]),
            (0, 6): sum(x_dist[:-1]) + 2 * x_dist[-2] + sum(y_dist) + sum(y_dist[:2]),
            (0, 7): sum(x_dist) + 2 * sum(y_dist[:2]),
            (1, 2): x_dist[3] + sum(y_dist[1:3]),
            (1, 3): x_dist[4] + sum(y_dist[1:3]),
            (1, 4): sum(x_dist[2:4]) + y_dist[3],
            (1, 5): sum(x_dist[2:4]) + y_dist[2],
            (1, 6): sum(x_dist[4:6]) + y_dist[3],
            (1, 7): sum(x_dist[4:]) + y_dist[2],
            (2, 3): sum(x_dist[3:5]) + 2 * y_dist[0],
            (2, 4): 2 * x_dist[1] + x_dist[2] + sum(y_dist[1:]),
            (2, 5): x_dist[2] + y_dist[1],
            (2, 6): sum(x_dist[3:-1]) + sum(y_dist[1:]),
            (2, 7): sum(x_dist[3:]) + y_dist[1],
            (3, 4): sum(x_dist[2:5]) + sum(y_dist[1:]),
            (3, 5): sum(x_dist[1:5]) + x_dist[1] + 2 * y_dist[0] + y_dist[1],
            (3, 6): x_dist[5] + sum(y_dist[1:]),
            (3, 7): sum(x_dist[5:]) + y_dist[1],
            (4, 5): 2 * x_dist[1] + sum(y_dist[2:]),
            (4, 6): sum(x_dist[2:-1]),
            (4, 7): sum(x_dist[2:]) + sum(y_dist[2:]),
            (5, 6): sum(x_dist[1:-1]) + x_dist[1] + 2 * x_dist[5] + sum(y_dist) + sum(y_dist[:2]),
            (5, 7): sum(x_dist[1:]) + x_dist[1] + 2 * sum(y_dist[:2]),
            (6, 7): 2 * x_dist[5] + x_dist[-1] + sum(y_dist[2:])}
for i in range(8):
    for j in range(i):
        dist_map[i, j] = dist_map[j, i]  # complete dist_map using symmetric path values without a node to itself
# heuristic for A*
h = {(i, i): 0 for i in range(8)}
for k, v in dist_map.items():
    h[k] = v // 10  # dividing by 10 to avoid overestimation

# implement A* to find shortest path from each machine to all others
for source in range(7):
    for sink in range(source + 1, 8):
        task_2_a_star(dist_map, h, source, sink)

# for convenience in gurobi, convert keys in dist_map s.t. 0~5: machines, 6: delivery, -1: warehouse
dist_map_gb = {(k[0] - 1, k[1] - 1): v for k, v in dist_map.items()}

# shortest transportation time from every node to all others in second
tt_map = {k: v / spd for k, v in dist_map_gb.items()}

# solve using gurobi
task_2_gurobi(test_case[0], time_limit, tt_map)

# check shortest path solution
nodes = [f'Machine {i}' for i in range(1, 7)]
nodes.append('Delivery')
nodes.insert(0, 'Warehouse')
print('\n*******************************************'
      '\n****** Shortest path solution below *******'
      '\n*******************************************\n')
for source in range(7):
    for sink in range(source + 1, 8):
        print(f'{nodes[source]} <-> {nodes[sink]}: {dist_map[source, sink]}')

# check gurobi solution
print('\n*******************************************'
      '\n********** Gurobi solution below **********'
      '\n*******************************************\n')
for case in test_case:
    case.dtl = dtl_flag
    print(case)
