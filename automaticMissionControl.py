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
from A_Star import A_Star, direction
from CreateRobotCommands import CreateRobotCommands
from MQTTread import MQTTread
from MQTTwrite import MQTTwrite 
from detectMarkers import detectMarkers
from FindTargets import FindTargets


def automaticMissionControl():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)

    # Create the grid map
    map_grid, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y, grid_size_width, grid_size_height = create_grid_map()

    # check if the grid map was created successfully
    if map_grid is None:
        print("Failed to create the grid map.")
        return
    
    print ("Grid map created successfully!")
    print(map_grid)

    time.sleep(1)

    # expand highground area
    expansion_size = 1
    rows, cols = len(map_grid), len(map_grid[0])
    grid = np.array(map_grid)  # Create a copy of the grid to avoid modifying the original

    # Identify highground cells
    highground_cells = [(i, j) for i in range(rows) for j in range(cols) if grid[i][j] == 1]

    # Expand highground area
    for i, j in highground_cells:
        for di in range(-expansion_size, expansion_size + 1):
            for dj in range(-expansion_size, expansion_size + 1):
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    grid[ni][nj] = 1
    print ("Highground area expanded successfully!")
    print (grid)

    # Initialize the camera feed
    camera_feed = cv2.VideoCapture(0)  # Change 0 to the path of your video file if needed

    if not camera_feed.isOpened():
        print("Failed to open camera or video file.")
        return

    babyspice_detected = False
    correct_orientation = False

    while not babyspice_detected or not correct_orientation:
        ret, frame = camera_feed.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Convert the frame to grayscale for ArUco detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers and their poses using the existing detectMarkers function
        corners, ids, tvecs = detectMarkers(gray)

        # Display the frame with detected markers and IDs
        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imshow('Mission Control Feed', frame)

            # BabySpice detection logic
            if ids is not None and 7 in ids.flatten():
                marker_index = np.where(ids == 7)[0][0]
                marker_corners = corners[marker_index]

                # Calculate the center of the detected marker
                marker_center = np.mean(marker_corners[0], axis=0)
                marker_x, marker_y = int(marker_center[0]), int(marker_center[1])

                print(f"BabySpice's position: (X: {marker_x}, Y: {marker_y})")

                # Convert pixel position to grid coordinates
                grid_x = int((marker_x - min_x) / (pixels_per_cm_x * 50))  # grid_size is 5 cm
                grid_y = int((marker_y - min_y) / (pixels_per_cm_y * 50))

                print(f"BabySpice's grid position: (Row: {grid_y}, Col: {grid_x})")

                current_pos = [grid_x, grid_y]

                # Calculate the orientation of the marker
                # The orientation can be determined by the angle of the line connecting two corners
                corner_0 = marker_corners[0][0]  # First corner
                corner_1 = marker_corners[0][1]  # Second corner
                dx = corner_1[0] - corner_0[0]
                dy = corner_1[1] - corner_0[1]
                angle = np.degrees(np.arctan2(dy, dx))
                # Current orientation of the robot
                # Round the angle to the nearest multiple of 10 degrees
                current_dir = round(angle / 5) * 5

                # Check if orientation is correct
                if current_dir !=270:
                    print("Error: BabySpice is not facing the correct direction.")
                    correct_orientation = False
                else:
                    print("BabySpice is ready to start the mission!")
                    print("Starting position:", current_pos)
                    correct_orientation = True

            else:
                print("BabySpice not detected - please put her in frame!")
                babyspice_detected = False
                correct_orientation = False

        # Display the frame
        cv2.imshow('Mission Control Feed', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    time.sleep(5)

    print("Calculating the path of BabySpice to collect all the spice and return to the starting point.")

    # Release camera feed and close all OpenCV windows
    camera_feed.release()
    cv2.destroyAllWindows()


    #find best order to hit spice_targets
    start = current_pos
    spice_targets = FindTargets(grid, 2)
    HG_targets = FindTargets(grid, 1)

    permutations = []
    length = [[] for _ in range(len(spice_targets) * (len(spice_targets) - 1) * (len(spice_targets) - 2))]
    total_length = []
    # Initialize event_grid
    event_grid = np.zeros((len(map_grid), len(map_grid[0])))

    # Generate permutations of spice targets
    for i in range(len(spice_targets)):
        for j in range(len(spice_targets)):
            if j != i:
                for k in range(len(spice_targets)):
                    if k != i and k != j:
                        permutations.append((start, spice_targets[i], spice_targets[j], spice_targets[k], start))

    # Calculate path lengths for each permutation
    for a in range(len(permutations)):
        for b in range(len(permutations[a]) - 1):
            length[a].append(len(A_Star(permutations[a][b], permutations[a][b + 1], map_grid)))
        total_length.append(sum(length[a]))

    # Choose the permutation with the shortest total length
    chosen_permutation = permutations[total_length.index(min(total_length))]

    print(chosen_permutation)

    # Find and store path for all spice_targets combined
    path = []

    for i in range(len(chosen_permutation) - 1):
        path.append(A_Star(chosen_permutation[i], chosen_permutation[i + 1], grid))

    for i in range(len(path)):
        j = 1

    # Initialize the camera feed and other variables
    camera_feed = cv2.VideoCapture(0)  # Change 0 to the path of your video file if needed
    i = 0
    j = 0
    worm_trigger = 0 #default
    worm_trigger_counter = 0 #default
    last_checked_time = 0  # Initialize last check time
    check_interval = 5  # 3 seconds between checks

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

                    # Display the frame with detected markers and IDs
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

                        # Convert pixel position to grid coordinates
                        grid_x = int((marker_x - min_x) / (pixels_per_cm_x * 5)) # grid_size is 5 cm
                        grid_y = int((marker_y - min_y) / (pixels_per_cm_y * 5))

                        # Update the current position of the robot
                        current_pos = [grid_x, grid_y]

                        # Calculate the orientation of the marker
                        # The orientation can be determined by the angle of the line connecting two corners
                        corner_0 = marker_corners[0][0]  # First corner
                        corner_1 = marker_corners[0][1]  # Second corner
                        dx = corner_1[0] - corner_0[0]
                        dy = corner_1[1] - corner_0[1]
                        angle = np.degrees(np.arctan2(dy, dx))
                        # current orientation of the robot
                        # round the angle to the nearest multiple of 90 degrees 
                        current_dir = round(angle / 90) * 90
                        # if output is 360, set it to 0
                        if current_dir == 360:
                            current_dir = 0
                        
                    else:
                        print("BabySpice not detected - please put her in frame!")

                        # Check if the sandworm (marker 5) is in frame
                        sandworm_present = False
                        if ids is not None:
                            sandworm_present = 5 in ids.flatten()  # Check for sandworm marker

                        if sandworm_present:
                            worm_trigger = 1
                            print ("Worm detected, redirecting to high ground")
                        else:
                            worm_trigger = 0

                    # if q is pressed, exit the loop
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                #check if the target has been reached
                # current position can be within 1 cell of the target
                # this is to account for any errors in the robot's movement
                if current_pos[0] in range(current_target[0]-1, current_target[0]+2) and current_pos[1] in range(current_target[1]-1, current_target[1]+2):

                    #check if worm trigger is on
                    if worm_trigger == 1:
                        worm_trigger_counter += 1

                        #check if it is the first time the worm trigger has been on
                        if  worm_trigger_counter == 1:
                            
                            #find closest high ground
                            distance_to_HG = []
                            for k in range(len(HG_targets)):
                                distance_to_HG.append(len(A_Star(current_pos, HG_targets[k], event_grid)))
                            chosen_HG = HG_targets[distance_to_HG.index(min(distance_to_HG))]
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

        # if q is pressed, exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
                    
        
    print("All spice collected and returned to start")


    # Release camera feed and close all OpenCV windows
    camera_feed.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
     # This code will only run if this file is executed directly
     automaticMissionControl()
