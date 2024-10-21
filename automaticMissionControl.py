# this file is the main file for the automatic mission control
"""
automaticMissionControl.py
This file is the main file for the automatic mission control. It is responsible for running the automatic mission control system.
Functions:
    automaticMissionControl(): Executes the automatic mission control sequence, 
    including creating a grid map, monitoring for sandworm presence, and managing the mission's progress.
Usage:
    This script should be executed directly to run the automatic mission control.
"""
# it will be responsible for the following:
# running the automatic mission control

# import the necessary libraries
import time
import cv2

# import the necessary functions
from makeGridMap import create_grid_map
from captureImage import captureImage
from planPath import plan_path
from monitorBSandSW import monitor_sandworm_and_babyspice

def automaticMissionControl():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Automatic is starting started!")

    # Create the grid map
    map_grid, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y = create_grid_map()

    print(map_grid)

    if map_grid is not None:
        # Pass the map and parameters to the next function
        plan_path(map_grid)
    else:
        print("Failed to create grid map.")
        return

    # Initialize collected_spice and camera_feed
    collected_spice = set()
    
    # Initialize the camera feed (use 0 for the default camera or provide a video file path)
    camera_feed = cv2.VideoCapture(0)  # Change 0 to the path of your video file if needed

    if not camera_feed.isOpened():
        print("Failed to open camera or video file.")
        return

    # Read the first frame to get the dimensions
    ret, frame = camera_feed.read()
    if not ret:
        print("Failed to read from camera or video file.")
        return

    # Start monitoring sandworm presence and BabySpice's position
    monitor_sandworm_and_babyspice(camera_feed, map_grid, collected_spice, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y)

if __name__ == "__main__":
    # This code will only run if this file is executed directly
    automaticMissionControl()
