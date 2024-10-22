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
import numpy as np
import cv2.aruco as aruco


# import the necessary functions
from makeGridMap import create_grid_map
from captureImage import captureImage
from planPath import plan_path
from monitorBSandSW import monitor_sandworm_and_babyspice
from planPath import plan_path
from A_Star import A_Star
from CreateRobotCommands import CreateRobotCommands
from MQTTread import MQTTread
from MQTTwrite import MQTTwrite 
from detectMarkers import detectMarkers

# initialise variables
last_checked_time = 0  # Initialize last check time
check_interval = 3  # 3 seconds between checks


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
    
    # get path and high ground from plan_path
    path, high_ground = plan_path(map_grid)
    
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
    
    # Initialize the camera feed and other variables
    camera_feed = cv2.VideoCapture(0)  # Change 0 to the path of your video file if needed
    i = 0
    j = 0
    event_grid = np.zeros(len(grid), len(grid[0]))
    worm_trigger = 0 #default
    worm_trigger_counter = 0 #default

    if not camera_feed.isOpened():
        print("Failed to open camera or video file.")
        return

    # Read the first frame to get the dimensions
    ret, frame = camera_feed.read()
    if not ret:
        print("Failed to read from camera or video file.")
        return
    
    # Convert the frame to grayscale for ArUco detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect markers and their poses using the existing detectMarkers function
    corners, ids, tvecs = detectMarkers(gray)

    #reset variables
    current_target = path[i][j+1]


    while i <= len(path):
        while j < len(path[i]):
            executing_value = int(MQTTread("Executing"))
            if executing_value == 0:    
                while True:
                    current_time = time.time()

                    # Capture the current frame from the camera feed
                    ret, frame = camera_feed.read()

                    if not ret:
                        print("Failed to capture frame.")
                        break

                    # Convert the frame to grayscale for ArUco detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # Detect markers and their poses using the existing detectMarkers function
                    corners, ids, tvecs = detectMarkers(gray)

                    # Display the frame with detected markers and grid lines
                    if ids is not None:
                        aruco.drawDetectedMarkers(frame, corners, ids)
                    cv2.imshow('Mission Control Feed', frame)

                    # Perform checks and operations only if the interval has passed
                    if current_time - last_checked_time >= check_interval:
                        last_checked_time = current_time  # Update last check time

                    # Track BabySpice’s position (marker 4)
                    if ids is not None and 4 in ids.flatten():
                        marker_index = np.where(ids == 4)[0][0]
                        marker_corners = corners[marker_index]

                        # Calculate the center of the detected marker
                        marker_center = np.mean(marker_corners[0], axis=0)
                        marker_x, marker_y = int(marker_center[0]), int(marker_center[1])

                        print(f"BabySpice's position: (X: {marker_x}, Y: {marker_y})")

                        # Convert pixel position to grid coordinates
                        grid_x = int((marker_x - min_x) / (pixels_per_cm_x * 5))  # grid_size is 5 cm
                        grid_y = int((marker_y - min_y) / (pixels_per_cm_y * 5))

                        print(f"BabySpice's grid position: (Row: {grid_y}, Col: {grid_x})")
                        current_pos = [grid_x, grid_y]

                        # Calculate the orientation of the marker
                        # The orientation can be determined by the angle of the line connecting two corners
                        corner_0 = marker_corners[0][0]  # First corner
                        corner_1 = marker_corners[0][1]  # Second corner
                        dx = corner_1[0] - corner_0[0]
                        dy = corner_1[1] - corner_0[1]
                        angle = np.degrees(np.arctan2(dy, dx))

                        print(f"BabySpice's orientation: {angle:.2f} degrees")
                        current_dir = angle
                    else:
                        print("BabySpice not detected.")

                        # Check if the sandworm (marker 5) is in frame
                        sandworm_present = False
                        if ids is not None:
                            sandworm_present = 5 in ids.flatten()  # Check for sandworm marker

                        if sandworm_present:
                            worm_trigger = 1
                        else:
                            worm_trigger = 0

                    # if q is pressed, exit the loop
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                #check if the target has been reached
                if current_pos == current_target:

                    #check if worm trigger is on
                    if worm_trigger == 1:
                        worm_trigger_counter += 1

                        #check if it is the first time the worm trigger has been on
                        if  worm_trigger_counter == 1:
                            print ("Worm detected, redirecting to high ground")
                            #find closest high ground
                            distance_to_HG = []
                            for k in range(len(high_ground)):
                                distance_to_HG.append(len(A_Star(current_pos, high_ground[k], event_grid)))
                            chosen_HG = high_ground[distance_to_HG.index(min(distance_to_HG))]
                            #find path to HG and back to position before worm trigger
                            event_path = A_Star(current_pos, chosen_HG, event_grid)
                            a = 1
                            while a < len(event_path)-1:
                                if direction(path[a-1], path[a]) == direction(path[a], path[a+1]):
                                    event_path[a].remove(path[i][j])
                                else:
                                    a += 1
                            reverse_event_path = event_path.reverse() #need to check that this does what you want it to do
                            event_path.append(reverse_event_path)
                            event_path.remove(event_path[0])
                            #add to main path list
                            path[i][j+1:j+1] = event_path

                    #move on to next point and reset worm trigger counter
                    worm_trigger_counter = 0
                    j += 1

                #if the target has not been reached
                else:
                    MOTOR_DIRECTIONS, RPM, TIME = CreateRobotCommands(current_pos, current_dir, current_target)
                    MQTTwrite("M1_Dir", MOTOR_DIRECTIONS[0])
                    MQTTwrite("M2_Dir", MOTOR_DIRECTIONS[1])
                    MQTTwrite("M1_RPM", RPM)
                    MQTTwrite("M2_RPM", RPM)
                    MQTTwrite("TIME", TIME)
            else:
                print("Waiting for robot to finish executing order")

        print("Target reached, Collecting spice")
        #move on to next target set
        i += 1
        j = 0
                
        
    print("All spice collected and returned to start")


    # Release camera feed and close all OpenCV windows
    camera_feed.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # This code will only run if this file is executed directly
    automaticMissionControl()
