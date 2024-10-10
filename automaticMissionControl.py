# this file is the main file for the automatic mission control
# it will be responsible for the following:
# running the automatic mission control

# import the necessary libraries
import time

# define the function
def automaticMissionControl():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Automatic mission started!")

# run
if __name__ == "__main__":
    # This code will only run if this file is executed directly
    automaticMissionControl()
