import time
import random
from z3 import *


def single_robot_brick(bs_ps, ps, bs_class=None):
    """
    solver for tower of hanoi problem
    :param bs_ps: initial and target config of bricks-positions in a dict as {b1:(p1,p1_),b2:(p2,p2_),...}
    :param ps: number of positions
    :param bs_class: classes of bricks, None for unique bricks
    :return min_ts: minimum number of times/steps
            et: execution time
    """

    # params
    start_time = time.time()
    bs = len(bs_ps)
    ts = math.ceil(3 * bs / 2)  # maximum number of steps in theory

    # model for task 1
    s = Optimize()

    # decision variables
    x = [[[Bool(f'on_{b}_{p}_{t}') for t in range(ts + 1)] for p in range(ps)] for b in range(bs)]
    y = [[Bool(f'obj_{b}_{t}') for t in range(ts)] for b in range(bs)]
    z = [Int(f'cnt_{t}') for t in range(ts)]
    m = [[Bool(f'from_{p}_{t}') for t in range(ts)] for p in range(ps)]
    n = [[Bool(f'to_{p}_{t}') for t in range(ts)] for p in range(ps)]

    # constraints
    # 1. precondition: if any brick is at p_ -> cannot move b to p_
    precon = [Implies(And(x[b][p][t], Or([x[b_][p_][t] for b_ in range(bs) if b != b_])),
                      Not(And(y[b][t], n[p_][t])))
              for t in range(ts) for b in range(bs) for p in range(ps) for p_ in range(ps) if p != p_]
    s.add(precon)
    # 2. uniqueness of m (from)
    unique_m = [Implies(And(x[b][p][t], y[b][t]),
                        And(m[p][t], And([Not(m[p_][t]) for p_ in range(ps) if p != p_])))
                for t in range(ts) for b in range(bs) for p in range(ps)]
    s.add(unique_m)
    # 3. uniqueness of n (to)
    unique_n = [n[p][t] == And([Not(n[p_][t]) for p_ in range(ps) if p != p_])
                for t in range(ts) for p in range(ps)]
    s.add(unique_n)
    # 4. uniqueness of y (obj)
    unique_y = [PbLe([(y[b][t], 1) for b in range(bs)], 1) for t in range(ts)]
    s.add(unique_y)
    # 5. non-moving bricks
    non_moving = [Implies(And(Not(y[b][t]), x[b][p][t]),
                          And(x[b][p][t + 1], And([Not(x[b][p_][t + 1]) for p_ in range(ps) if p != p_])))
                  for t in range(ts) for b in range(bs) for p in range(ps)]
    s.add(non_moving)
    # 6. distinct of m (from) and n (to)
    distinct_m_n = [Implies(m[p][t],
                            Not(n[p][t]))
                    for t in range(ts) for p in range(ps)]
    s.add(distinct_m_n)
    # 7. update
    update = [Implies(And(y[b][t], m[p][t], n[p_][t]),
                      And(x[b][p_][t + 1], And([Not(x[b][p__][t + 1]) for p__ in range(ps) if p_ != p__])))
              for t in range(ts) for b in range(bs) for p in range(ps) for p_ in range(ps) if p != p_]
    s.add(update)
    # 8. initial and final state
    if bs_class:  # bricks with classes
        state = [And(x[b][p[0]][0], Or([x[b][p_[1]][ts] for b_, p_ in bs_ps.items() if b_ in cls]))
                 for cls in bs_class for b, p in bs_ps.items() if b in cls]
    else:  # unique bricks
        state = [And(x[b][p[0]][0], x[b][p[1]][ts])
                 for b, p in bs_ps.items()]
    s.add(state)
    # 9. count steps at each time instance
    count = And([z[t] == sum([If(Or([y[b][t] for b in range(bs)]), 1, 0)]) for t in range(ts)])
    s.add(count)

    # objective
    objective = Sum(z)
    s.minimize(objective)

    # solve
    s.check()

    # get result
    min_ts = sum([s.model()[z[t]].as_long() for t in range(ts)])

    return min_ts, time.time() - start_time


def test_case(bs, ps, bs_class_num=0):
    """
    randomly generate a test case
    :param bs: number of bricks
    :param ps: number of positions
    :param bs_class_num: classes of bricks, 0 for unique bricks
    :return: bs_ps dict
             bs_class list
    """

    # randomly generate brick-position pairs
    assert bs < ps, 'Positions must be more than bricks!'
    ps_list = [i for i in range(ps)]
    org, tag = random.sample(range(ps), bs), []
    for i in range(bs):
        p = random.choice(ps_list)
        while p == org[i]:
            p = random.choice(ps_list)
        tag.append(p)
        ps_list.remove(p)

    # randomly and equally split into different classes if required
    bs_class = []
    if bs_class_num:
        assert bs_class_num <= bs, 'Class number must be no more than bricks!'
        bs_list = [i for i in range(bs)]
        num = bs // bs_class_num
        for i in range(bs_class_num):
            if i == bs_class_num - 1:  # the last round
                cls = tuple(bs_list)
            else:
                cls = tuple(random.sample(bs_list, num))
                for each in cls:
                    bs_list.remove(each)
            bs_class.append(cls)

    return {i: (org[i], tag[i]) for i in range(bs)}, bs_class


def main():
    # test: unique bricks
    print('******************** Unique bricks ********************')
    for bs in range(1, 8):
        ps = bs + 1
        bs_ps, _ = test_case(bs, ps)
        min_ts, et = single_robot_brick(bs_ps, ps)
        print(f'{bs} unique bricks and {ps} positions, solvable within {min_ts} steps, '
              f'execution time: {int(et / 60)}min {int(et % 60)}sec {int(1e3 * et % 1e3)}ms')

    # test: bricks with classes
    print('******************** Bricks with classes ********************')
    for bs in range(3, 8):
        ps = bs + 1
        cls_num = random.choice(range(2, bs))
        bs_ps, bs_class = test_case(bs, ps, bs_class_num=cls_num)
        min_ts, et = single_robot_brick(bs_ps, ps, bs_class=bs_class)
        print(f'{bs} bricks in {cls_num} classes and {ps} positions, solvable within {min_ts} steps, '
              f'execution time: {int(et / 60)}min {int(et % 60)}sec {int(1e3 * et % 1e3)}ms')


if __name__ == '__main__':
    main()
