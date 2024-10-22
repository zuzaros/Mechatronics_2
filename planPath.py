from FindTargets import FindTargets
from A_Star import A_Star, direction

# this function is used to plan the path of babyspice
# it is an excert from Marina's code


def plan_path(map_grid):

    print("Calculating the path of BabySpice to collect all the spice and return to the starting point.")

    grid=map_grid

    #find best order to hit spice_targets
    start = (0,0)
    spice_targets = FindTargets(grid, 2)
    HG_targets = FindTargets(grid, 1)
    permutations = []
    length = [[],[],[],[],[],[]]
    total_length = []

    for i in range(len(spice_targets)):
        for j in range(len(spice_targets)):
            if j != i:
                for k in range(len(spice_targets)):
                    if k != i and k != j:
                        permutations.append((start, spice_targets[i], spice_targets[j], spice_targets[k], start))

    for a in range(len(permutations)):
        for b in range(len(permutations[0])-1):
            length[a].append(len(A_Star(permutations[a][b], permutations[a][b+1], grid)))
        total_length.append(sum(length[a]))

    chosen_permutation = permutations[total_length.index(min(total_length))]

    print(chosen_permutation)

    #find and store path for all spice_targets combined
    path = []

    for i in range(len(chosen_permutation)-1):
        path.append((A_Star(chosen_permutation[i], chosen_permutation[i+1], grid)))

    for i in range(len(path)):
        j = 1
        while j < len(path[i])-1:
            if direction(path[i][j-1], path[i][j]) == direction(path[i][j], path[i][j+1]):
                path[i].remove(path[i][j])
            else:
                j += 1


    return path, HG_targets


        