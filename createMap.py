import matplotlib.pyplot as plt

def createMap(highground, spice, sand, babySpice, sandworm):
    fig, ax = plt.subplots()
    
    # Plot highground areas
    if highground is not None:
        for coord in highground:
            ax.plot(coord[0][0][0], coord[0][0][1], 'ro', label="Highground")
    
    # Plot spice areas
    if spice is not None and len(spice) > 0:
        spice_x, spice_y = zip(*[(pt[0][0], pt[0][1]) for pt in spice])
        ax.scatter(spice_x, spice_y, c='yellow', label="Spice", s=10)
    
    # Plot sand areas
    if sand is not None and len(sand) > 0:
        sand_x, sand_y = zip(*[(pt[0][0], pt[0][1]) for pt in sand])
        ax.scatter(sand_x, sand_y, c='brown', label="Sand", s=10)

    # Plot babySpice's position
    if babySpice is not None:
        ax.plot(babySpice[0][0][0], babySpice[0][0][1], 'bx', label="babySpice", markersize=10)
    
    # Plot sandworm's position
    if sandworm is not None:
        ax.plot(sandworm[0][0][0], sandworm[0][0][1], 'gx', label="sandworm", markersize=10)

    ax.set_title("Environment Map")
    ax.legend()
    plt.show()