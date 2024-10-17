# this file is the main file for the automatic mission control
# it will be responsible for the following:
# running the automatic mission control

# import the necessary libraries
import time

# import the necessary functions
from captureImage import captureImage

# define the function
def automaticMissionControl():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Automatic is starting started!")

    # call function to capture camera feed, process it and capture map

    # keep checking if sandworm is in the frame
    # if sandworm is in the frame, call function to move babySpice to highground
    # if sandworm is not in the frame, call function to make babySpice follow the planned trajectory
    # check if all spice is collected
    # if all spice is collected, call function to end the mission
    # end the mission
    print('All spice collected. Mission complete!')

# run
if __name__ == "__main__":
    # This code will only run if this file is executed directly
    automaticMissionControl()
