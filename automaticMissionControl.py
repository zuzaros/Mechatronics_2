# this file is the main file for the automatic mission control
"""
automaticMissionControl.py
This file is the main file for the automatic mission control. It is responsible for running the automatic mission control system.
Functions:
    automaticMissionControl(): Executes the automatic mission control sequence, including creating a grid map, monitoring for sandworm presence, and managing the mission's progress.
Usage:
    This script should be executed directly to run the automatic mission control.
"""
# it will be responsible for the following:
# running the automatic mission control

# import the necessary libraries
import time

# import the necessary functions
from makeGridMap import create_grid_map

def next_function(map_grid):
    # Process the map grid
    print("Processing map grid...")
    # Add your processing code here

def main():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Automatic is starting started!")

    # create the grid map
    map_grid = create_grid_map()

    print(map_grid)

    if map_grid is not None:
    # Pass the map grid to the next function
        next_function(map_grid)
    else:
        print("Failed to create grid map.")

    # keep checking if sandworm is in the frame
    # if sandworm is in the frame, call function to move babySpice to highground
    # if sandworm is not in the frame, call function to make babySpice follow the planned trajectory
    # check if all spice is collected
    # if all spice is collected, call function to end the mission
    # end the mission
    print('All spice collected. Mission complete!')



if __name__ == "__main__":
    # This code will only run if this file is executed directly
    main()
