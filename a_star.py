import gridworld
from ai import *
from math import *
from queue import PriorityQueue

#-------------A* pathfinding algorithms--------------
# NOTE: All A* are based off of sequential-heuristic.
#       We use h = inf as a dummy heuristic to make
#       the supplemental heuristics useless

# Default A*
# map: Gridworld terrain map
# start: Tuple representing start coordinates in (x, y)
# goal: Tuple representing goal coordinates in (x, y)
def default(map, start, goal):
    return weighted(map, start, goal, 1)

# Weighted
# map: Gridworld terrain map
# start: Tuple representing start coordinates in (x, y)
# goal: Tuple representing goal coordinates in (x, y)
# h: Heuristic function, default h_pythagorean
# w: Weight, default 1.0
def weighted(map, start, goal, w=1, h = h_pythagorean):
    return sequential(map, start, goal, w, 1, [h, lambda **kwa: inf])

# Uniform-cost
# map: Gridworld terrain map
# start: Tuple representing start coordinates in (x, y)
# goal: Tuple representing goal coordinates in (x, y)
def uniform(map, start, goal):
    return weighted(map, start, goal, 0, h_uniform_first) 

# Sequential-Heuristic
# map: Gridworld terrain map
# start: Tuple representing start coordinate in (x, y)
# goal: Tuple representing goal coordinate in (x, y)
# w: Overall weight, default 1.25
# w2: Inadmissable-favored weight, default 2
# list_h: List of heuristic functions to iterate over, list_h[0] is the anchor heuristic
def sequential(map, start, goal, w = 1.25, w2 = 2, list_h = all_heuristics):
    rows = len(map)
    cols = len(map[0])
    n_h = len(list_h)
    expansions = 0
    fringes = [PriorityQueue() for i in range(5)]
    closed = []
    
    parent_set = {k: {i: {j: None for j in range(cols)} for i in range(rows)} for k in range(n_h)}
    f_set = {k: {i: {j: inf for j in range(cols)} for i in range(rows)} for k in range(n_h)}
    g_set = {k: {i: {j: inf for j in range(cols)} for i in range(rows)} for k in range(n_h)}
    h_set = {k: {i: {j: list_h[k](start = start, goal = goal, v = (j, i)) for j in range(cols)} for i in range(rows)} for k in range(n_h)}

    for i in range(n_h):
        f_set[i][start[1]][start[0]] = 0 + w * h_set[i][start[1]][start[0]]
        g_set[i][start[1]][start[0]] = 0
        fringes[i].put((f_set[i][start[1]][start[0]], start))

    while fringes[0].queue[0][0] < inf:
        for k in range(1, n_h):
            minkey = fringes[0].queue[0][0]
            minkey2 = fringes[k].queue[0][0]

            # 0th key or ith key has the current smallest fscore 
            min_i = k if minkey2 <= w2 * minkey else 0

            fringe = fringes[min_i]
            parent = parent_set[min_i]
            f = f_set[min_i]
            g = g_set[min_i]
            h = h_set[min_i]

            pop = fringe.get() 
            s = pop[1]

            if g[goal[1]][goal[0]] <= pop[0] and g[goal[1]][goal[0]] < inf:  # End goal 
                s = goal 
                ret = {'f': f, 'g': g, "h": h, 'map': [s]}
                print("Expansions: ", expansions)

                while parent[s[1]][s[0]] != None:
                    s = parent[s[1]][s[0]]
                    ret['map'].insert(0, s)
                    
                return ret

            for i in range(max(0, s[1] - 1), min(rows, s[1] + 2)):
                for j in range(max(0, s[0] - 1), min(cols, s[0] + 2)):
                    s_p = (j, i)

                    if s_p == s:
                        continue

                    g_temp = g[s[1]][s[0]] + cost(map, s, s_p)

                    if s_p not in closed and g_temp < g[i][j]:
                        parent[i][j] = s
                        g[i][j] = g_temp
                        f[i][j] = g[i][j] + w * h[i][j]
                        expansions += 1
                        in_fringe = False
                        with fringe.mutex:
                            in_fringe = s_p in fringe.queue

                        if not in_fringe:
                            fringe.put((f[i][j], s_p))

    print("failed")
    return None
