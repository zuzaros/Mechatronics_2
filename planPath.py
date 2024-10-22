

from A_Star import A_Star

# this function is used to plan the path of babyspice
# it is an excert from Marina's code


def plan_path(map_grid):

    print("Calculate the path of BabySpice to collect all the spice and return to the starting point.")

    #initialise variables
    start = (0,0)
    permutations = []
    length = [[],[],[],[],[],[]]
    total_length = []

    # write function to make grid map with only 1s and 0s, make all 2s, 3s and 4s into 0s
    grid = map_grid.copy()  # Create a copy to avoid modifying the original grid
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 2 or grid[i][j] == 3 or grid[i][j] == 4:
                grid[i][j] = 0

    # find high ground coordinates and store them in a list
    high_ground = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 1:
                high_ground.append((i,j))

    print (grid)
    
    # find centre of spice fields and set it as targets

    targets = [(0,4), (2,1), (4,3)]

    #find best order to hit targets
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

    return path, high_ground


        