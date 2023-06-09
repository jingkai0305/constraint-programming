import numpy as np
import csv


# class for better processing test cases
class TestCase:
    def __init__(self, name, size, pt, po, slv='To be solved', time='To be solved', obj='To be solved',
                 sch='To be solved', dtl=False):
        """
        :param name: name of test case
        :param size: (n jobs * m machines)
        :param pt: process time p_ij in second
        :param po: processing order of each job
        :param slv: solver: gurobi or z3
        :param time: execution time of the solver
        :param obj: optimal objective in second
        :param sch: schedule solution (start time) in second
        :param dtl: detail flag when printing
        """
        self.name = name
        self.size = size
        self.pt = pt
        self.po = po
        self.slv = slv
        self.time = time
        self.obj = obj
        self.sch = sch
        self.dtl = dtl

    def __str__(self):
        info = f'Case name: {self.name}\n' \
               f'Number of jobs: {self.size[0]}\n' \
               f'Number of machines: {self.size[1]}\n' \
               f'Processing time:\n{self.pt}\n' \
               f'Processing order:\n{self.po}\n' \
               f'Solver: {self.slv}\n' \
               f'Time: {self.time}\n' \
               f'Optimal objective: {self.obj}\n' \
               f'Schedule (start time):\n{self.sch}\n' \
            if self.dtl else \
            f'Case name: {self.name}\n' \
            f'Solver: {self.slv}\n' \
            f'Time: {self.time}\n' \
            f'Optimal objective: {self.obj}\n' \
            f'Schedule (start time):\n{self.sch}\n'
        return info


def read_test_case(case_name):
    # (temp) container for all test cases
    cases_temp, cases = [], []

    # read all test cases into cases
    for each in case_name:
        with open(f'.\Test case\{each}.txt', newline='') as f:
            cases_temp.append(list(csv.reader(f)))

    # process test cases format
    for case in cases_temp:
        name = case[2][0].split(' ')[-1]
        size = tuple(map(int, case[6][0].split(' ')[1:]))
        pt, po = np.zeros(size, dtype=int), np.zeros(size, dtype=int)
        for i, each in enumerate(case[7:]):
            single_job = list(filter(lambda a: a != '', each[0].split(' ')))
            for j in range(0, len(single_job), 2):
                po[i, int(j / 2)] = single_job[j]
                pt[i, int(single_job[j])] = int(single_job[j + 1])
        cases.append(TestCase(name, size, pt, po))

    return cases
