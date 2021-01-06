import random
import math
import os

random.seed()

start = (-1, -1)
goal = (-1, -1)
terrain = []

c_hardregions = () 

# Vertex represents one cell in the terrain
# As per the spec in the assignment, terrain is marked with a character 
# - 0: blocked
# - 1: unblockd
# - 2: hard to traverse
# - a: unblocked highway
# - b: hard to traverse highway
# Helper methods are provided to make getting info easier, 
# as well as highway marking

class Vertex:
    __code = '1'
    
    def __init__(self, c):
        self.__code = c

    def isHighway(self):
        return self.__code == 'a' or self.__code == 'b'
    
    def isBlocked(self):
        return self.__code == '0'

    def isUnblocked(self):
        return self.__code == '1' or self.__code == 'a'

    def isHardToTraverse(self):
        return self.__code == '2' or self.__code == 'b'

    def markHighway(self):
        if self.__code == '1':
            self.__code = 'a'
        elif self.__code == '2':
            self.__code = 'b'

    def unmarkHighway(self):
        if self.__code == 'a':
            self.__code = '1'
        elif self.__code == 'b':
            self.__code = '2' 

    def markUnblocked(self):
        self.__code = '1'

    def markHardToTraverse(self):
        self.__code = '2'
 
    def markBlocked(self):
        self.__code = '0'   
    
    def __repr__(self): 
        return f"{self.__code}"

# Init terrain as follows:
# - Define a grid map 1 cell bigger with all blocked cells
# - Create a slice within the map that represents the inner area; modify this slice only
# - Select 8 random regions to be partially blocked
# - Create 4 highways
# - Select 20% of the total number of cells to be blocked cells
# For more information, see section 2 of assignment.pdf
def initTerrain(rows = 120, cols = 160):
    # Save total number of cells for later use
    size = rows * cols
    
    # Initialize cells to be blocked 
    ret = [[Vertex('0') for _ in range(cols + 2)] for _ in range(rows + 2)] 
 
    # Select the internal section to be unblocked.
    # We will modify this map.
    t = [[ret[i][j] for j in range(1, cols + 1)] for i in range(1, rows + 1)]
    for row in t:
        for v in row:
            v.markUnblocked()    

    # Select random partially blocked cells 
    for _ in range(8):
        global c_hardregions

        x = random.randrange(cols - 1)    
        y = random.randrange(rows - 1)
  
        c_hardregions += ((x, y),)
  
        t_slice = [t[y][x - 15:x + 15] for y in range(max(y - 15, 0), min(y + 15, rows))] 
        
        for row in t_slice:
            for v in row:
                random.choice([v.markHardToTraverse, v.markUnblocked])()
    
    # Create "highways"
    # NOTE: Assume after 10 tries that highways cannot be generated given the current config
    # 
    # 1 - Pick someplace on the edge
    # 2 - Pick a random direction
    # 3 - Push tile to list
    # 4 - Move in direction
    # 5 - Check if tile is a valid tile, if not break
    # 6 - Loop back to #3 19 more times
    # 7 - If 20 tiles have just been pushed to list, 60% chance of choosing a new direction, 20% of each perpendicular direction
    # 8 - Check number of tiles and stopping point. If both are valid, mark
    #     as a success, commit all as highway, and move on to the next one 
    highways = () 
    while len(highways) < 4:
        x = -1
        y = -1
        cur_highway = ()
        cur_state = 0
        n_tries = 10
        dir = random.randrange(4)

        while True:
            if bool(random.getrandbits(1)):
                x = random.randrange(cols)
                y = random.choice([0, rows - 1])
            else:
                x = random.choice([0, cols - 1])
                y = random.randrange(rows)
        
            if not t[y][x].isHighway():
                break

        while True:
            if cur_state == 0: # walk
                t[y][x].markHighway()

                cur_highway += (t[y][x],)
                 
                if len(cur_highway) % 20 == 0: # Change direction in 20-cell segments
                    dir += random.choice([0, 0, 0, 1, 3])
                    dir %= 4
                    n_cells = 0

                if dir == 0: # North
                    y -= 1
                elif dir == 2: # South
                    y += 1
                elif dir == 1: # West
                    x -= 1
                else: # Default to East
                    dir = 3
                    x += 1
              
                # Check if we end this highway builder
                if not 0 <= x < cols or not 0 <= y < rows or t[y][x].isHighway():
                    cur_state = 1

            elif cur_state == 1: # Check if highway is valid
                if (
                    len(cur_highway) < 100
                    or (
                        x in range(cols)
                        and y in range(rows)
                        and t[y][x].isHighway()
                    )
                ):
                    cur_state = 2
                else:
                    cur_state = 3

            elif cur_state == 2: # Highway is invalid, restart
                n_tries -= 1 
                if n_tries == 0:
                    for hw in highways:
                        for v in hw:
                            v.unmarkHighway()

                    highways = ()
                else: 
                    for v in cur_highway:
                        v.unmarkHighway()

                cur_highway = ()
                break

            elif cur_state == 3: # Success, add highway to list
                for v in cur_highway:
                    v.markHighway()

                highways += (cur_highway,)
                break

    # Generate "walls"
    for _ in range(int(size * 0.2)):
        while True: 
            v = t[random.randrange(rows)][random.randrange(cols)]
       
            if not v.isHighway() and not v.isBlocked():
                v.markBlocked() 
                break

    for i in range(rows + 2):
        for j in range(cols + 2):
            ret[i][j].coordinates = (i, j)

    return ret 

def writeGridworld(path):
    global terrain, start, goal, c_hardregions
    with open(path, 'w') as f:
        f.write(f"{start[0]} {start[1]}" + os.linesep)
        f.write(f"{goal[0]} {goal[1]}" + os.linesep)

        for r in c_hardregions:
            f.write(f"{r[0]} {r[1]}" + os.linesep)
        
        for row in terrain:
            f.write(''.join([repr(v) for v in row]) + os.linesep)     

def loadGridworld(path):
    global terrain, start, goal, c_hardregions
    with open(path) as f:
        start = tuple(int(x) for x in f.readline().split(' '))
        goal = tuple(int(x) for x in f.readline().split(' '))

        c_hardregions = ()
        for _ in range(8):
            c_hardregions += (tuple(int(x) for x in f.readline().split(' ')),)

        terrain = []
        for line in f:
            print(line)
            terrain += [[Vertex(x) for x in line], ]

        print(terrain)

def initGridworld(rows = 120, cols = 160):
    global terrain, start, goal 
    terrain = initTerrain(rows, cols)
    
    while True:
        start = [random.randrange(cols) + 1, random.randrange(rows) + 1]
        goal = [random.randrange(cols) + 1, random.randrange(rows) + 1]
        
        if (
            sum([(a - b) ** 2 for a, b in zip(start, goal)]) >= 10000 
            and not terrain[start[1]][start[0]].isBlocked() 
            and not terrain[goal[1]][goal[0]].isBlocked()
        ):
            break
