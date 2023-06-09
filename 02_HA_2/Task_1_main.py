from Read_test_case import *
from Task_1_helper_functions import *

# numpy is needed in helper functions

# select test cases from folder "Test case", see details in Read_test_case.py
case_name = ['tf06', 'tf10', 'la01', 'la02', 'la03', 'la04', 'la05']

# read all required test cases into a list containing Test_case objects
test_case = read_test_case(case_name)

# params
time_limit = 20  # time limit for solver in min
dtl_flag = False  # detail flag of Test_case, True for detailed info, False for solution only when printing

# solve using gurobi
for case in test_case:
    task_1_gurobi(case, time_limit)
# check solutions
print('\n*******************************************'
      '\n********** Gurobi solution below **********'
      '\n*******************************************\n')
for case in test_case:
    case.dtl = dtl_flag
    print(case)

# solve using z3
for case in test_case:
    task_1_z3(case, time_limit)
# check solutions
print('\n*******************************************'
      '\n************ Z3 solution below ************'
      '\n*******************************************\n')
for case in test_case:
    case.dtl = dtl_flag
    print(case)
