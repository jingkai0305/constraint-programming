import time
from z3 import *
from Task_2 import test_case


def multi_robot_brick(rs, bs_ps, ps, bs_class=None):
    """
    solver for tower of hanoi problem
    :param rs: number of robots
    :param bs_ps: initial and target config of bricks-positions in a dict as {b1:(p1,p1_),b2:(p2,p2_),...}
    :param ps: number of positions
    :param bs_class: classes of bricks, None for unique bricks
    :return min_ts: minimum number of times/steps
            et: execution time
    """

    # params
    start_time = time.time()
    bs = len(bs_ps)
    ts = math.ceil(3 * bs / 2 / rs)  # maximum number of steps in theory

    # model for task 1
    s = Optimize()

    # decision variables
    x = [[[Bool(f'on_{b}_{p}_{t}') for t in range(ts + 1)] for p in range(ps)] for b in range(bs)]
    y = [[[Bool(f'obj_{r}_{b}_{t}') for t in range(ts)] for b in range(bs)] for r in range(rs)]
    z = [Int(f'cnt_{t}') for t in range(ts)]
    m = [[Bool(f'from_{p}_{t}') for t in range(ts)] for p in range(ps)]
    n = [[Bool(f'to_{p}_{t}') for t in range(ts)] for p in range(ps)]

    # constraints
    # 1. precondition: if any brick is at p_ -> cannot move b to p_
    precon = [Implies(And(x[b][p][t], Or([x[b_][p_][t] for b_ in range(bs) if b != b_])),
                      And([Not(And(y[r][b][t], n[p_][t])) for r in range(rs)]))
              for t in range(ts) for b in range(bs) for p in range(ps) for p_ in range(ps) if p != p_]
    s.add(precon)
    # 2. unique m (from)
    unique_m = [Implies(And(x[b][p][t], Or(y[r][b][t] for r in range(rs))),
                        And(m[p][t], PbLe([(m[p_][t], 1) for p_ in range(ps) if p != p_], rs - 1)))
                for t in range(ts) for b in range(bs) for p in range(ps)]
    s.add(unique_m)
    # 3. uniqueness of n (to)
    unique_n = [n[p][t] == PbLe([(n[p_][t], 1) for p_ in range(ps) if p != p_], rs - 1)
                for t in range(ts) for p in range(ps)]
    s.add(unique_n)
    # 4. uniqueness of y (obj) TBC
    unique_y = [PbLe([(y[r][b][t], 1) for b in range(bs) for r in range(rs)], rs) for t in range(ts)]
    s.add(unique_y)
    pp(unique_y)
    # 5. non-moving bricks
    non_moving = [Implies(And(Not(Or([y[r][b][t] for r in range(rs)])), x[b][p][t]),
                          And(x[b][p][t + 1], And([Not(x[b][p_][t + 1]) for p_ in range(ps) if p != p_])))
                  for t in range(ts) for b in range(bs) for p in range(ps)]
    s.add(non_moving)
    # 6. distinct of m (from) and n (to)
    distinct_m_n = [Implies(And(m[p][t], y[r][b][t]),
                            Not(And(n[p][t], y[r][b][t])))
                    for t in range(ts) for b in range(bs) for p in range(ps) for r in range(rs)]
    s.add(distinct_m_n)
    # 7. update
    update = [Implies(And(y[r][b][t], m[p][t], n[p_][t]),
                      And(x[b][p_][t + 1], And([Not(x[b][p__][t + 1]) for p__ in range(ps) if p_ != p__])))
              for t in range(ts) for b in range(bs) for p in range(ps) for p_ in range(ps) for r in range(rs)
              if p != p_]
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
    count = [And(z[t] == sum([If(Or([y[r][b][t] for r in range(rs)]), 1, 0) for b in range(bs)])) for t in range(ts)]
    s.add(count)

    # objective
    objective = Sum(z)
    s.minimize(objective)

    # solve
    s.check()

    # get result
    min_ts = sum([s.model()[z[t]].as_long() for t in range(ts)])

    return min_ts, time.time() - start_time


def main():
    rs = 3
    bs = 3
    ps = 4
    bs_ps, _ = test_case(bs, ps)
    multi_robot_brick(rs, bs_ps, ps, bs_class=None)


if __name__ == '__main__':
    main()
