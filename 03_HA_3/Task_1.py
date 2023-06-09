from z3 import *


def toh(ds, tws):
    """
    solver for tower of hanoi problem
    :param ds: number of disks
    :param tws: number of towers
    :return min_ts: minimum number of times/steps
    """

    # params
    ts = 2 ** ds  # maximum number of steps

    # model for task 1
    s = Optimize()

    # decision variable
    x = [[[Bool(f'on_{d}_{tw}_{t}') for t in range(ts + 1)] for tw in range(tws)] for d in range(ds)]
    y = [[Bool(f'obj_{d}_{t}') for t in range(ts)] for d in range(ds)]
    z = [Int(f'cnt_{t}') for t in range(ts)]
    m = [[Bool(f'from_{tw}_{t}') for t in range(ts)] for tw in range(tws)]
    n = [[Bool(f'to_{tw}_{t}') for t in range(ts)] for tw in range(tws)]

    # constraints
    # 1. precondition 1
    precon_1 = [Implies(And(x[d][tw][t], Or([x[d_][tw][t] for d_ in range(d)])),
                        Not(y[d][t]))
                for t in range(ts) for d in range(ds) for tw in range(tws)]
    s.add(precon_1)
    # 2. precondition 2
    precon_2 = [Implies(And(x[d][tw][t], Or([x[d_][tw_][t] for d_ in range(d)])),
                        Not(And(y[d][t], n[tw_][t])))
                for t in range(ts) for d in range(ds) for tw in range(tws) for tw_ in range(tws) if tw != tw_]
    s.add(precon_2)
    # 3. uniqueness of m (from)
    unique_m = [Implies(And(x[d][tw][t], y[d][t]),
                        And(m[tw][t], And([Not(m[tw_][t]) for tw_ in range(tws) if tw != tw_])))
                for t in range(ts) for d in range(ds) for tw in range(tws)]
    s.add(unique_m)
    # 4. uniqueness of n (to)
    unique_n = [n[tw][t] == And([Not(n[tw_][t]) for tw_ in range(tws) if tw != tw_])
                for t in range(ts) for tw in range(tws)]
    s.add(unique_n)
    # 5. uniqueness of y (obj)
    unique_y = [PbLe([(y[d][t], 1) for d in range(ds)], 1) for t in range(ts)]
    s.add(unique_y)
    # 6. non-moving disks
    non_moving = [Implies(And(Not(y[d][t]), x[d][tw][t]),
                          And(x[d][tw][t + 1], And([Not(x[d][tw_][t + 1]) for tw_ in range(tws) if tw != tw_])))
                  for t in range(ts) for d in range(ds) for tw in range(tws)]
    s.add(non_moving)
    # 7. distinct of m (from) and n (to)
    distinct_m_n = [Implies(m[tw][t],
                            Not(n[tw][t]))
                    for t in range(ts) for tw in range(tws)]
    s.add(distinct_m_n)
    # 8. update
    update = [Implies(And(y[d][t], m[tw][t], n[tw_][t]),
                      And(x[d][tw_][t + 1], And([Not(x[d][tw__][t + 1]) for tw__ in range(tws) if tw_ != tw__])))
              for t in range(ts) for d in range(ds) for tw in range(tws) for tw_ in range(tws) if tw != tw_]
    s.add(update)
    # 9. initial and final state
    state = [And(x[d][0][0], x[d][tws - 1][ts])
             for d in range(ds)]
    s.add(state)
    # 10. count steps at each time instance
    count = And([z[t] == sum([If(Or([y[d][t] for d in range(ds)]), 1, 0)]) for t in range(ts)])
    s.add(count)

    # objective
    objective = Sum(z)
    s.minimize(objective)

    # solve
    s.check()

    # get result
    min_ts = sum([s.model()[z[t]].as_long() for t in range(ts)])

    return min_ts


def main():
    # compare z3 results with groundtruth
    for ds in range(3, 8):
        min_ts_true = 2 ** ds - 1
        min_ts_z3 = toh(ds, 3)
        print(f"Given {ds} disks and 3 towers, what's the minimum number of steps?")
        print(f'In theory: {min_ts_true}\tZ3: {min_ts_z3}\n')


if __name__ == '__main__':
    main()
