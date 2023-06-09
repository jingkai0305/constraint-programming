from Task_3_helper_functions import *

# params
time_limit = 20  # time limit for solver in min
source, sink = 5, 3
path_num = 10  # number of paths to be found

# info
# x-direction distance of shop floor, left to right, in meter
x_dist = [7, 21, 25, 20, 18, 28, 8]
# y-direction distance of shop floor, bottom to top, in meter
y_dist = [17, 17, 17, 19]
# initialize distance from a node to others, 1~6: machines, 0: warehouse, 7: delivery
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

# solve using Z3
all_path = task_3_exhaustive_dijkstra(dist_map, source, sink, time_limit, path_num)

# check solutions
print('\n*********************************************'
      '\n********** 10 shortest paths below **********'
      '\n*********************************************\n')
for i in range(1, path_num + 1):
    print(f'No.{i}:\t{all_path[i][0]},\t{all_path[i][1]}')
