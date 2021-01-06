import gridworld
from math import *

#------------Heuristic Algorithms-------------
# NOTE: Using kwargs to define abstract heuristics function
#       Use the following key schema for params:
#       - start: start vertex 
#       - goal:  goal vertex
#       - v:     current vertex

# Pythagorean distance between current vertex and goal
def h_pythagorean(**kwargs):
    goal = kwargs['goal']
    v = kwargs['v']

    return sum((a - b) ** 2 for a, b in zip(goal, v)) ** 0.5

# Manhattan distance between current vertex and goal
def h_manhattan(**kwargs):
    goal = kwargs['goal']
    v = kwargs['v']

    return sum(abs(a - b) for a, b in zip(goal, v))

# Farthest distance from goal in one axis
def h_axis_dist(**kwargs):
    goal = kwargs['goal']
    v = kwargs['v']

    return max(abs(a - b) for a, b in zip(goal, v))

# Manhattan distance on a hex grid
def h_manhattan_hex(**kwargs):
    goal = kwargs['goal']
    v = kwargs['v']

    return abs(sum((a - b) for a, b in zip(goal, v))) / len(v) 

# Custom heuristic using the distance from the start as the heuristic
def h_delta(**kwargs):
    start = kwargs['start']
    goal = kwargs['goal']
    v = kwargs['v']

    totalDist = sum((a - b) ** 2 for a, b in zip(goal, start)) ** 0.5
    startDist = sum((a - b) ** 2 for a, b in zip(v, start)) ** 0.5
    return abs(totalDist - startDist)

# Uniform-first "heuristic"
# Simply makes all h-values 0
def h_uniform_first(**kwargs):
    return 0

# Internally, maintain a list of all the usable heuristics functions
all_heuristics = [
    h_pythagorean,
    h_manhattan,
    h_manhattan_hex,
    h_axis_dist,
    h_delta
]

def isAdmissible (hCur, hParent, cost):
    return hParent <= cost + hCur

def cost(map, s, s_prime):
    v = map[s[1]][s[0]]
    v_prime = map[s_prime[1]][s_prime[0]]
    ret = inf

    if v.isBlocked() or v_prime.isBlocked():  # You cannot transition between blocked cells
        return ret

    f_v = 1
    f_vp = 1

    if not any(a == b for a, b in zip(s, s_prime)):  # Diagonal
        f_v = sqrt(2)
        f_vp = sqrt(2)

    elif v.isHighway() and v_prime.isHighway():  # On a highway
        f_v /= 4
        f_vp /= 4

    f_v *= 2 if v.isHardToTraverse() else 1
    f_vp *= 2 if v_prime.isHardToTraverse() else 1

    ret = f_v + f_vp
    ret /= 2

    return ret
