import heapq

#heuristic function using manhattan distance
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#A* algorithm
def A_Star(start, end, grid):
    
    #initialize the open and closed lists
    OpenList = []
    ClosedList = []
    #create dictionaries to store the cost of the path, the heuristic cost and the total cost for each node
    parent = {}
    g = {start: 0} #the cost of getting from the start node to that node
    h = {start: heuristic(start, end)} #heuristic cost of getting from the node to the goal
    f = {start: g[start] + h[start]} #the total cost of getting from the start node to the goal by passing by that node

    #add the start node into the open list
    heapq.heappush(OpenList, (f[start], start))

    while OpenList:
        #set current node = node with smallest f in OpenList and pop from OpenList
        current = heapq.heappop(OpenList)[1]
        if current == end:
            #reconstruct the path
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            return path
        else:
            #add current to the ClosedList
            ClosedList.append(current)

            #Expand current by finding and exploring neighbors, can not move diagonally
            for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                #change this part to my own code
            
                #checks neighbor is within the grid and is not an obstacle
                #assumes non-obstacles are 0 and obstacles are 1 in grid
                if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]) and grid[neighbor[0]][neighbor[1]] != 1:
                    #calculate tentative g
                    tentative_g = g[current] + 1

                    #if neighbor is in the ClosedList and tentative_g >= g[neighbor], skip
                    #otherwise, update the parent, g, f and push into the OpenList
                    if neighbor not in g or tentative_g < g[neighbor]:
                        parent[neighbor] = current
                        g[neighbor] = tentative_g
                        h[neighbor] = heuristic(neighbor, end)
                        f[neighbor] = g[neighbor] + h[neighbor]
                        heapq.heappush(OpenList, (f[neighbor], neighbor))
    else:
        return 'No path found'

#test
start = (0, 0)
#end = (4, 0)
grid = [[0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]]

#find best order to hit targets
targets = [(0,4), (2,1), (4,3)]
permutations = []
length = [[],[],[],[],[],[]]
total_length = []

for i in range(len(targets)):
    for j in range(len(targets)):
        if j != i:
            for k in range(len(targets)):
                if k != i and k != j:
                    permutations.append((start, targets[i], targets[j], targets[k], start))

for a in range(len(permutations)):
    for b in range(len(permutations[0])-1):
        length[a].append(len(A_Star(permutations[a][b], permutations[a][b+1], grid)))
    total_length.append(sum(length[a]))

chosen_permutation = permutations[total_length.index(min(total_length))]

print(chosen_permutation)

#find and store path for all targets combined
path = []

for i in range(len(chosen_permutation)-1):
    path.append((A_Star(chosen_permutation[i], chosen_permutation[i+1], grid)))

print(path)

#only keep important points (start, targets and turning points)
def direction(a, b): #a is the first coordinate, b is the second coordinate
    if a[0] == b[0]:
        if a[1] < b[1]:
            return 0 #right
        else:
            return 180 #left
    else:
        if a[0] < b[0]:
            return 90 #up
        else:
            return 270 #down

for i in range(len(path)):
    j = 1
    while j < len(path[i])-1:
        if direction(path[i][j-1], path[i][j]) == direction(path[i][j], path[i][j+1]):
            path[i].remove(path[i][j])
        else:
            j += 1

print(path)


