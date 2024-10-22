def FindTargets(grid, number):

    #find all points that are identified_targets
    identified_targets = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == number]

    #find all bottom left corners of identified_targets
    bottom_left_corners = []

    for coord in identified_targets:
        i, j = coord
        if i < len(grid) - 1 and j > 0:
            if grid[i - 1][j] == number and grid[i][j + 1] == number and grid[i + 1][j] != number and grid[i][j - 1] != number:
                bottom_left_corners.append(coord)

    #only keep bottom left corners of identified_targets
    identified_targets = bottom_left_corners

    return identified_targets

# only run the following code if this file is run as the main file

if __name__ == "__main__":
    FindTargets()
