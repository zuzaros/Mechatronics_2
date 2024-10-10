# this file is the main file for the manual mission control
# it will be responsible for the following:
# running the manual mission control

# import the necessary libraries
import time

# define the runMission function
def manualMissionControl():
    print("Running manual mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Manual Mission started!")

# run
if __name__ == "__main__":
    # This code will only run if this file is executed directly
    manualMissionControl()
